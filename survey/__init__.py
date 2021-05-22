import time

from otree.api import *


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
        choices=['unter 17', '18-20', '21-30', '31-40', '41-50', '51-60', 'älter als 60'],
        label='Bitte geben Sie an, welcher Altersgruppe Sie angehöre.',

    )

    student = models.StringField(
        choices=[['Ja', 'Ja'], ['Nein', 'Nein']],
        label='Studieren Sie derzeit an einer Universität bzw. Hochschule?',
        widget=widgets.RadioSelect,
    )

    origin = models.StringField(
        choices=[['Ja', 'Ja'], ['Nein', 'Nein']],
        label='Sind Sie und beide Elternteile mit deutscher Staatsangehörigkeit geboren?',
        widget=widgets.RadioSelect,
    )
    family = models.StringField(
        choices=['Ledig', 'Verheiratet', 'Geschieden', 'Verwitwet'],
        label='Bitte geben Sie Ihren Familienstand an.',
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
    form_fields = ['age', 'student', 'origin', 'family']

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
