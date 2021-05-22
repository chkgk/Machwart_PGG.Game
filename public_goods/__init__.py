from otree.api import *

import time
import random

doc = """
This is a one-period public goods game with 3 players.
"""


class Constants(BaseConstants):
    name_in_url = 'public_goods'
    players_per_group = 3
    num_others_per_group = players_per_group - 1
    num_rounds = 2
    instructions_template = 'public_goods/instructions.html'
    # """Amount allocated to each player"""
    endowment = cu(20)
    multiplier = 1.2
    # """drop out settings""" #
    max_group_match_waiting = 600  # seconds
    page_timeout = 120  # seconds


class Subsession(BaseSubsession):
    def creating_session(self):
        for p in self.get_players():
            p.participant.vars['dropout'] = False

    @staticmethod
    def group_by_arrival_time_method(self, waiting_players):
        # successful group building:
        if len(waiting_players) >= Constants.players_per_group:
            return waiting_players[:Constants.players_per_group]


        for p in waiting_players:
            if p.matching_takes_too_long():
                p.participant.vars['dropout'] = True
                return [p]


class Group(BaseGroup):
    total_contribution = models.CurrencyField()
    individual_share = models.CurrencyField()


class Player(BasePlayer):
    def matching_takes_too_long(player):
        now = time.time()
        return now - player.participant.vars.get('wait_page_arrival', now) > Constants.max_group_match_waiting

    contribution = models.CurrencyField(
        min=0,
        max=Constants.endowment,
        doc="""The amount contributed by the player""",
        label="Wie viele Punkte möchten Sie zum öffentlichen Projekt beitragen (min. 0, max. 20)?",
    )


# FUNCTIONS
def vars_for_admin_report(subsession: Subsession):
    contributions = [p.contribution for p in subsession.get_players() if p.contribution != None]
    if contributions:
        return dict(
            avg_contribution=sum(contributions) / len(contributions),
            min_contribution=min(contributions),
            max_contribution=max(contributions),
        )
    else:
        return dict(
            avg_contribution='(no data)',
            min_contribution='(no data)',
            max_contribution='(no data)',
        )


def set_payoffs(group: Group):
    group.total_contribution = sum([p.contribution for p in group.get_players()])
    group.individual_share = (
            group.total_contribution * Constants.multiplier / Constants.players_per_group
    )

    for p in group.get_players():
        p.payoff = (Constants.endowment - p.contribution) + group.individual_share


def set_payment_round(player: Player):
    player.payment_round = random.randint(1, Constants.num_rounds)


# PAGES
class PGG_InitialWaitPage(WaitPage):
    template_name = 'public_goods/PGG_InitialWaitPage.html'
    group_by_arrival_time = True

    def app_after_this_page(player: Player, upcoming_apps):
        # in the case of someone waiting too long at the waiting page:
        if player.participant.vars.get('dropout'):
            player.participant.vars['payment_round'] = 0
            player.participant.vars['payment_round_payoff'] = 0
            player_list = player.group.get_players()
            for p in player_list:
                if p.participant.vars.get('dropout'):
                    for p2 in player_list:
                        p2.participant.vars['dropout_in_group'] = True
            return upcoming_apps[-1]
        else:
            return

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


class Contribute(Page):
    """Player: Choose how much to contribute"""

    form_model = 'player'
    form_fields = ['contribution']

    def vars_for_template(player: Player, **kwargs):
        other_players = player.get_others_in_group()
        other_players_ages = [p.participant.vars['age'] for p in other_players]
        other_players_studentinfo = [p.participant.vars['student'] for p in other_players]
        other_players_origin = [p.participant.vars['origin'] for p in other_players]
        other_players_family = [p.participant.vars['family'] for p in other_players]
        i = 0
        for p in other_players:
            player.participant.vars[f'age{i}'] = other_players_ages[i]
            player.participant.vars[f'student{i}'] = other_players_studentinfo[i]
            player.participant.vars[f'origin{i}'] = other_players_origin[i]
            player.participant.vars[f'family{i}'] = other_players_family[i]
            i += 1

    def get_timeout_seconds(player: Player):
        if player.participant.vars.get('dropout'):
            return 1  # instant timeout, 1 second
        else:
            return Constants.page_timeout

    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:
            player.participant.vars['dropout'] = True


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs
    body_text = "Bitte warten Sie auf die Entscheidungen der übrigen Gruppenmitglieder."


class Results(Page):
    """Players payoff: How much each has earned"""


    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return dict(total_earnings=group.total_contribution * Constants.multiplier,
                    average_contribution=(group.total_contribution - player.contribution) /
                                         (Constants.players_per_group - 1))

    def get_timeout_seconds(player: Player):
        if player.participant.vars.get('dropout'):
            return 1  # instant timeout, 1 second
        else:
            return Constants.page_timeout

    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:
            player.participant.vars['dropout'] = True
        # in the last round a random round and its payoff will be selected for every player
        if player.round_number == Constants.num_rounds:
            payment_round = random.randint(1, Constants.num_rounds)
            player.participant.vars['payment_round'] = payment_round
            player.participant.vars['payment_round_payoff'] = player.in_round(payment_round).payoff
            player_list = player.group.get_players()
            for p in player_list:
                if p.participant.vars.get('dropout'):
                    for p2 in player_list:
                        p2.participant.vars['dropout_in_group'] = True


page_sequence = [PGG_InitialWaitPage, Contribute, ResultsWaitPage, Results]
