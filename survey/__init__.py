import time

from otree.api import *

c = Currency  # old name for currency; you can delete this.


class Constants(BaseConstants):
    name_in_url = 'survey'
    num_rounds = 1
    Endowment = 20
    multiplier = 1.2
    num_others_per_group = 0
    players_per_group = None


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    age = models.StringField(
        choices=['18-30', '31-40', '41-50', '51-60', 'älter als 60'],
    )

    student = models.StringField(
        choices=[['Ja', 'Ja'], ['Nein', 'Nein']],
        widget=widgets.RadioSelectHorizontal,
    )

    origin = models.StringField(
        choices=[['Ja', 'Ja'], ['Nein', 'Nein']],
        widget=widgets.RadioSelectHorizontal,
    )
    family = models.StringField(
        choices=['Ledig', 'Verheiratet', 'Geschieden', 'Verwitwet'],
    )
    gender = models.StringField(
        choices=['weiblich', 'männlich'],
        widget=widgets.RadioSelectHorizontal,
    )
    ethnic = models.StringField(
        choices=['Nordeuropa', "Westeuropa", "Mitteleuropa", "Osteuropa", "Südeuropa", "Afrika", "Asien", "Nordamerika",
                 "Südamerika", "Australien"],
    )
    trust = models.StringField(
        choices=['Man kann den meisten Menschen vertrauen', 'Man kann nicht vorsichtig genug sein'],
        widget=widgets.RadioSelectHorizontal,
    )
    moral = models.StringField(
        choices=[
            [1, "1"],
            [2, "2"],
            [3, "3"],
            [4, "4"],
            [5, "5"],
            [6, "6"],
            [7, "7"],
            [8, "8"],
            [9, "9"],
            [10, "10"],
        ],
        widget=widgets.RadioSelectHorizontal,
    )
    altruism = models.StringField(
        choices=[
            [1, "Vollkommen ähnlich"],
            [2, "Sehr ähnlich"],
            [3, "Ziemlich ähnlich"],
            [4, "Etwas ähnlich"],
            [5, "Kaum ähnlich"],
            [6, "Gar nicht ähnlich"],
        ],
        widget=widgets.RadioSelectHorizontal,
    )
    Religion = models.StringField(
        choices=[
            [1, "1"],
            [2, "2"],
            [3, "3"],
            [4, "4"],
            [5, "5"],
            [6, "6"],
            [7, "7"],
            [8, "8"],
            [9, "9"],
            [10, "10"]],
        widget=widgets.RadioSelectHorizontal,
    )
    Experience = models.StringField(
        choices=[['Ja', 'Ja'], ['Nein', 'Nein']],
        widget=widgets.RadioSelectHorizontal,
    )

    CQ1 = models.IntegerField(blank=True)

    CQ2 = models.IntegerField(blank=True)

    CQ3 = models.IntegerField(blank=True)


# FUNCTIONS

# PAGES
class Willkommen(Page):
    form_model = 'player'


class Allgemeines(Page):
    form_model = 'player'


class Demographics(Page):
    form_model = 'player'
    form_fields = ['age', 'student', 'origin', 'family', 'gender', 'ethnic', 'trust', 'moral', 'altruism', 'Religion',
                   'Experience']

    def before_next_page(player: Player, **kwargs):
        player.participant.vars['age'] = player.age
        player.participant.vars['student'] = player.student
        player.participant.vars['origin'] = player.origin
        player.participant.vars['family'] = player.family
        player.participant.wait_page_arrival = time.time()
        player.participant.vars['dropout'] = False
        player.participant.vars['dropout_in_group'] = False


class Anleitung(Page):
    form_model = 'player'


# Error_Messages
def CQ1_error_message(self, value):
    if value != Constants.Endowment:
        return 'Rechnung: (20 Punkte – 0 Punkte) + (0.4 * 0 Punkte)'


def CQ2_error_message(self, value):
    if value != Constants.Endowment * Constants.multiplier:
        return 'Rechnung: (20 Punkte – 20 Punkte) + (0.4 * 60 Punkte)'


def CQ3_error_message(self, value):
    if value != Constants.Endowment + (
            2 * Constants.Endowment * Constants.multiplier) / 3:
        return 'Rechnung: (20 Punkte – 0) + (0.4 * 40 Punkte)'


class Fragen(Page):
    form_model = 'player'
    form_fields = [
        "CQ1", "CQ2", "CQ3"
    ]


page_sequence = [Willkommen, Allgemeines, Anleitung, Fragen, Demographics]
