from otree.api import *

import settings

c = Currency  # old name for currency; you can delete this.


doc = """
This application provides a webpage instructing participants how to get paid.
Examples are given for the lab and Amazon Mechanical Turk (AMT).
"""


class Constants(BaseConstants):
    name_in_url = 'payment_info'
    players_per_group = None
    num_rounds = 1
    participation_fee = 3


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    dropout = models.BooleanField()
    dropout_in_group = models.BooleanField()
    payment_round = models.IntegerField(min=0, max=Constants.num_rounds)
    payment_round_payoff = models.CurrencyField()


# FUNCTIONS
def set_dropout(player: Player):
    player.dropout = player.participant.vars['dropout']


def set_dropout_in_group(player: Player):
    player.dropout_in_group = player.participant.vars['dropout_in_group']


def set_payment_round(player: Player):
    player.payment_round = player.participant.vars['payment_round']


def set_payment_round_payoff(player: Player):
    player.payment_round_payoff = player.participant.vars['payment_round_payoff']


def set_payoff(player: Player):
    if not player.dropout_in_group:
        player.payoff = Constants.participation_fee + player.payment_round_payoff * 0.25
    else:
        if not player.dropout:
            player.payoff = Constants.participation_fee
        elif player.payment_round == 0:
            player.payoff = Constants.participation_fee
        else:
            player.payoff = 0


# PAGES
class PaymentInfo(Page):

    def is_displayed(player: Player):
        set_dropout(player)
        set_dropout_in_group(player)
        set_payment_round(player)
        set_payment_round_payoff(player)
        set_payoff(player)
        return True

    def vars_for_template(player: Player):
        return dict(
            final_payoff=(player.payment_round_payoff + 12).to_real_world_currency(player.session),
        )

page_sequence = [PaymentInfo]
