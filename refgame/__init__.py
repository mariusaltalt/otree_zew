from otree.api import (
    Page,
    WaitPage,
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range,
)
# To clean and commend - new stuff #
class Constants(BaseConstants):
    name_in_url = 'refgame'
    players_per_group = 4
    num_rounds = 2
    endowment = c(100)
    alpha = 4.4  # parameter for benefits from private account
    beta = 0.02  # parameter for benefits from private account
    gamma = 1  # parameter for benefits from public account
    tau = 100  # parameter to calibrate payoff
    instructions_template = 'refgame/instr_content.html'


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    total_contribution = models.CurrencyField()
    avg_contribution = models.CurrencyField()
    individual_share = models.CurrencyField()
    avg_payoff = models.CurrencyField()


class Player(BasePlayer):
    # Control Questions
    cq_1 = models.IntegerField(  # control question 1 (cq_1)
        min=0)

    cq_2 = models.IntegerField(  # control question 2 (cq_2)
        min=0)

    cq_3 = models.IntegerField(  # control question 3 (cq_3)
        choices=[5, 10, 15, 20],
        widget=widgets.RadioSelect()
    )

    cq_4 = models.IntegerField(  # control question 4 (cq_4)
        choices=[
            [1, "ja"],
            [2, "nein"],
        ], widget=widgets.RadioSelect()
    )

    cq_5 = models.IntegerField(  # control question 5 (cq_5)
        choices=[0, 50, 70, 90, 100],
        widget=widgets.RadioSelect()
    )

    cq_6 = models.IntegerField(  # control question 6 (cq_6)
        choices=[
            [1, "Aus den 5x5=25 Runden wird eine Runde ausgelost und ausgezahlt."],
            [2, "Eine der fünf Phasen, die aus fünf Runden bestehen, wird ausgelost und ausgezahlt"],
            [3, "Alle 5x5=25 Runden werden ausgezahlt"],
        ], widget=widgets.RadioSelect()
    )

    # Contribution
    contribution = models.CurrencyField(
        min=0, max=Constants.endowment, label="",
    )

    # Cumulative payoff
    cum_payoff = models.CurrencyField()

    # Avg. contribution other group members
    avg_contribution_others = models.CurrencyField()

# FUNCTIONS

# Payoff function
def set_payoffs(group):
    players = group.get_players()
    contributions = [p.contribution for p in players]
    group.total_contribution = sum(contributions)
    group.avg_contribution = sum(contributions) / Constants.players_per_group
    for p in players:  # avg. contributions of other group members
        p.avg_contribution_others = (group.total_contribution - p.contribution) / (Constants.players_per_group - 1)
    # group.avg_contribution = (group.total_contribution / Constants.players_per_group)
    # group.individual_share = (    # template payoff for linear public goods game
    #        group.total_contribution / Constants.players_per_group
    #)
    # for p in players:
    #    p.payoff = Constants.endowment - p.contribution + group.individual_share
    for p in players:  # payoff
        p.payoff = Constants.alpha * (Constants.endowment - p.contribution) - \
                   Constants.beta * (Constants.endowment - p.contribution) ** 2 \
                   + Constants.gamma * group.total_contribution - \
                   Constants.tau
    for p in players:  # cumulative payoff
        p.cum_payoff = sum([p.payoff for p in p.in_all_rounds()])
    group.avg_payoff = sum([p.payoff for p in players]) / Constants.players_per_group

# Error messages
def cq_1_error_message(player, value):  # error message cq_1
    if value != 294:
        return 'Die Antwort ist leider nicht korrekt. ' \
               'Die korrekte Antwort ist 4.4(100-20)-0.02(100-20)^2+(20+3*50)=352-128+170-100=294.'


def cq_2_error_message(player, value):  # error message cq_2
    if value != 164:
        return 'Die Antwort ist leider nicht korrekt. ' \
               'Die korrekte Antwort ist 4.4(100-60)-0.02(100-60)^2+(60+3*20)=176-32+120-100=164.'


def cq_3_error_message(player, value):  # error message cq_3
    if value != 15:
        return 'Die Antwort ist leider nicht korrekt. ' \
               'Die korrekte Antwort ist 15 mit einer Auszahlung in Höge von 189.5.'


def cq_4_error_message(player, value):  # error message cq_4
    if value != 2:
        return 'Die Antwort ist leider nicht korrekt. ' \
               'Selbst wenn die anderen nichts beitragen, ist es besser einen positiven Beitrag zu leisten' \
               '(beste Antwort ist immer 15)'


def cq_5_error_message(player, value):  # error message cq_5
    if value != 90:
        return 'Die Antwort ist leider nicht korrekt. ' \
               'Die korrekte Antwort ist 90 mit einer Auszahlung in Höge von 302.'


def cq_6_error_message(player, value):  # error message cq_6
    if value != 2:
        return 'Die Antwort ist leider nicht korrekt. ' \
               'Eine der fünf Phasen wird ausgelost und ausgezahlt.'

# PAGES

class Willkommen(Page):  # welcome page
    form_model = 'player'

    def is_displayed(player):  # welcome only once
        return player.round_number == 1


class Instruktionen(Page):  # Instructions
    form_model = "player"

    def is_displayed(player):  # instructions only once
        return player.round_number == 1


# Kontrollfragen
class Kontrollfragen(Page):  # Control questions
    form_model = "player"
    form_fields = ["cq_1", "cq_2", "cq_3", "cq_4", "cq_5", "cq_6"]

    def is_displayed(player):  # control questions only once
        return player.round_number == 1


# Und wie machen wir das mit der payoff table?

class Beitragsentscheidung(Page):
    form_model = 'player'
    form_fields = ['contribution']

    def is_displayed(player):
        return player.round_number <= Constants.num_rounds


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = 'set_payoffs'

    def is_displayed(player):
        return player.round_number <= Constants.num_rounds


class Results(Page):
    @staticmethod
    def vars_for_template(player):
        return dict(
                player1=player.group.get_player_by_id(1),
                player2=player.group.get_player_by_id(2),
                player3=player.group.get_player_by_id(3),
                player4=player.group.get_player_by_id(4),
        )


class FinalResults(Page):

    def is_displayed(player):  # control questions only once
        return player.round_number == Constants.num_rounds



page_sequence = [Willkommen,
                 Instruktionen,
                 Kontrollfragen,
                 Beitragsentscheidung,
                 ResultsWaitPage,
                 Results,
                 FinalResults]
