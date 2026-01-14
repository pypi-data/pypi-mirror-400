from .utils import format_snippet

def kr_swi_code():
    code = '''
is_a(ta, staff).
is_a(lecturer, staff).
is_a(lab_admin, staff).

instance_of(ali, student).
instance_of(sana, ta).
instance_of(hamza, lecturer).
instance_of(dr_faiza, lab_admin).
instance_of(bilal, student).
instance_of(zain, ta).

context(normal_day).
context(exam_day).

restricted(bilal).

on_duty(sana, exam_day).

% role resolution
has_role(Person, Role) :-
    instance_of(Person, CurrentRole),
    check_hierarchy(CurrentRole, Role).

check_hierarchy(Role, Role).
check_hierarchy(SubRole, SuperRole) :-
    is_a(SubRole, Intermediate),
    check_hierarchy(Intermediate, SuperRole).

% rules
can_enter(Person, _) :-
    restricted(Person), !, fail.

can_enter(Person, normal_day) :-
    has_role(Person, staff).

can_enter(Person, exam_day) :-
    has_role(Person, lecturer);
    has_role(Person, lab_admin).

can_enter(Person, exam_day) :-
    has_role(Person, ta),
    on_duty(Person, exam_day).

% final decision
decision(Person, Context, allow) :-
    can_enter(Person, Context), !.

decision(_, _, deny).

% testing
run_queries :-
    write('The staff on normal_day (hamza): '),
    decision(hamza, normal_day, D1),
    write(D1), nl,

    write('A student on normal_day (ali): '),
    decision(ali, normal_day, D2),
    write(D2), nl,

    write('TA on duty on exam_day (sana): '),
    decision(sana, exam_day, D3),
    write(D3), nl,

    write('TA not on duty on exam_day (zain): '),
    decision(zain, exam_day, D4),
    write(D4), nl,

    write('Non-TA student on exam_day (ali): '),
    decision(ali, exam_day, D6),
    write(D6), nl.

'''
    return format_snippet(code)

def kr_fuzzy_uni_code():
    code = '''
# Fuzzy uni

def tri(a, b, c, x):
    if x <= a or x >= c:
        return 0.0
    elif x == b:
        return 1.0
    elif x < b:
        return (x - a) / (b - a)
    else:
        return (c - x) / (c - b)

def toa_early(x):
    return tri(0, 1, 3, x)

def toa_normal(x):
    return tri(3, 5, 7, x)

def toa_late(x):
    return tri(7, 10, 10, x)

def pc_low(x):
    return tri(0, 1, 3, x)

def pc_medium(x):
    return tri(3, 5, 7, x)

def pc_high(x):
    return tri(7, 10, 10, x)

def access_allow(x):
    return tri(5, 7, 10, x)

def access_deny(x):
    return tri(0, 2, 5, x)

def fuzzify_toa(x):
    return toa_early(x), toa_normal(x), toa_late(x)

def fuzzify_pc(x):
    return pc_low(x), pc_medium(x), pc_high(x)

# ruel check
def apply_rules(toa_vals, pc_vals):
    early, normal, late = toa_vals
    low, medium, high = pc_vals

    R1 = min(late, low)
    R2 = min(normal, medium) 
    R3 = high

    print(f"R1 fired with strength {R1}")
    print(f"R2 fired with strength {R2}")
    print(f"R3 fired with strength {R3}")

    return R1, R2, R3

# aggregation + defuzzification
def defuzzify(R1, R2, R3):
    numerator = 0.0
    denominator = 0.0

    for x in range(0, 11):
        d1 = min(R1, access_deny(x))
        a2 = min(R2, access_allow(x))
        a3 = min(R3, access_allow(x))

        aggregated = max(d1, a2, a3)

        numerator += x * aggregated
        denominator += aggregated

    if denominator == 0:
        return 0.0
    return numerator / denominator

# crisp to label
def classify_access(x):
    allow = access_allow(x)
    deny = access_deny(x)

    if allow > deny:
        return "allow"
    else:
        return "deny"

# main
def main():
    time_of_access = 5
    criticality = 6

    print("Example Rule:")
    print(f"Time of access = {time_of_access}")
    print(f"Purpose criticality = {criticality}")

    toa_vals = fuzzify_toa(time_of_access)
    pc_vals = fuzzify_pc(criticality)

    R1, R2, R3 = apply_rules(toa_vals, pc_vals)
    crisp_output = defuzzify(R1, R2, R3)

    print(f"\nCrisp output value: {crisp_output:.4f}")
    print(f"Final decision: {classify_access(crisp_output)}")

main()

'''
    return format_snippet(code)

def kr_fuzzy_fan_code():
    code = '''
# Fuzzy Fan Speed (Smart Room / Temp Advisor)

def tri(a, b, c, x):
    if x <= a or x >= c:
        return 0.0
    elif x <= b:
        return (x - a) / (b - a)
    else:
        return (c - x) / (c - b)

def trap(a, b, c, d, x):
    if x <= a or x >= d:
        return 0.0
    elif b <= x <= c:
        return 1.0
    elif x < b:
        return (x - a) / (b - a)
    else:
        return (d - x) / (d - c)

# temp fuzzy
def temp_cold(t):
    return trap(0, 0, 10, 18, t)

def temp_warm(t):
    return tri(15, 22, 28, t)

def temp_hot(t):
    return trap(25, 30, 100, 100, t)

# fan speed funny
def fan_off(s):
    return trap(0, 0, 20, 35, s)

def fan_medium(s):
    return tri(30, 50, 70, s)

def fan_high(s):
    return trap(60, 80, 100, 100, s)


def fuzzify_temperature(t):
    cold = temp_cold(t)
    warm = temp_warm(t)
    hot = temp_hot(t)
    return cold, warm, hot

# defuzzification (Mamdani + Centroid)
def defuzzify(cold, warm, hot):
    numerator = 0.0
    denominator = 0.0

    for s in range(0, 101):
        r1 = min(cold, fan_off(s))
        r2 = min(warm, fan_medium(s))
        r3 = min(hot, fan_high(s))

        aggregated = max(r1, r2, r3)

        numerator += s * aggregated
        denominator += aggregated

    if denominator == 0:
        return 0.0
    return numerator / denominator

# final classification
def classify(speed):
    off = fan_off(speed)
    medium = fan_medium(speed)
    high = fan_high(speed)

    if off >= medium and off >= high:
        return "OFF"
    elif medium >= high:
        return "MEDIUM"
    else:
        return "HIGH"

# main
temperature = float(input("Enter room temperature (°C): "))

cold, warm, hot = fuzzify_temperature(temperature)
fan_speed = defuzzify(cold, warm, hot)
fan_label = classify(fan_speed)

print("\nFan Speed:", round(fan_speed, 2))
print("Fan Label:", fan_label)


'''
    return format_snippet(code)

def kr_bay_engine_code():
    code = '''
# Bayesian Engine
# given probability
P_low_oil = 0.2
P_no_low_oil = 0.8

# conditional prob
P_fail_given_low = 0.6
P_fail_given_no_low = 0.1

P_light_given_fail = 0.9
P_light_given_no_fail = 0.2


def prob_failure_given_light():
    # P(F ∧ L)
    p1 = P_light_given_fail * (
        P_fail_given_low * P_low_oil +
        P_fail_given_no_low * P_no_low_oil
    )

    # P(L)
    p_light = (
        P_light_given_fail *
        (P_fail_given_low * P_low_oil +
         P_fail_given_no_low * P_no_low_oil)
        +
        P_light_given_no_fail *
        ((1 - P_fail_given_low) * P_low_oil +
         (1 - P_fail_given_no_low) * P_no_low_oil)
    )

    return p1 / p_light


def prob_failure_given_light_and_low_oil():
    numerator = P_light_given_fail * P_fail_given_low * P_low_oil
    denominator = numerator + (
        P_light_given_no_fail *
        (1 - P_fail_given_low) *
        P_low_oil
    )
    return numerator / denominator


# main
p3 = prob_failure_given_light()
p4 = prob_failure_given_light_and_low_oil()

print("P(EngineFailure | EngineLight = On):", round(p3, 3))
print("P(EngineFailure | EngineLight = On, LowOil = Yes):", round(p4, 3))


'''
    return format_snippet(code)

def kr_bay_flu_code():
    code = '''
# Bayesian Flu
# given probability
P_flu = 0.1
P_not_flu = 0.9

# conditional Probability
P_fever_given_flu = 0.8
P_fever_given_not_flu = 0.2

P_cough_given_flu = 0.7
P_cough_given_not_flu = 0.3


def prob_flu_given_fever():
    numerator = P_fever_given_flu * P_flu
    denominator = (P_fever_given_flu * P_flu +
                   P_fever_given_not_flu * P_not_flu)
    return numerator / denominator


def prob_flu_given_fever_and_cough():
    numerator = (P_fever_given_flu *
                 P_cough_given_flu *
                 P_flu)

    denominator = numerator + (
        P_fever_given_not_flu *
        P_cough_given_not_flu *
        P_not_flu
    )

    return numerator / denominator


# main
p1 = prob_flu_given_fever()
p2 = prob_flu_given_fever_and_cough()

print("P(Flu | Fever = True):", round(p1, 3))
print("P(Flu | Fever = True, Cough = True):", round(p2, 3))


'''
    return format_snippet(code)

def kr_lab12_code():
    code = '''
#Lab 12
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination

model = DiscreteBayesianNetwork([
    ('Fever', 'Flu'),
    ('Cough', 'Flu'),
    ('Flu', 'TestResult')
])

# giveen probabilities
cpd_fever = TabularCPD(
    variable='Fever',
    variable_card=2,
    # false, true
    values=[[0.7], [0.3]]
)

cpd_cough = TabularCPD(
    variable='Cough',
    variable_card=2,
    values=[[0.6], [0.4]]
)

cpd_flu = TabularCPD(
    variable='Flu',
    variable_card=2,
    values=[
        [0.95, 0.6, 0.5, 0.1],  # flu = false
        [0.05, 0.4, 0.5, 0.9]   # flu = true
    ],
    evidence=['Fever', 'Cough'],
    evidence_card=[2, 2]
)

cpd_test = TabularCPD(
    variable='TestResult',
    variable_card=2,
    values=[
        [0.9, 0.2],  # neg
        [0.1, 0.8]   # pos
    ],
    evidence=['Flu'],
    evidence_card=[2]
)

model.add_cpds(cpd_fever, cpd_cough, cpd_flu, cpd_test)

assert model.check_model()
print("bayesian network created...\n")

inference = VariableElimination(model)

q1 = inference.query(variables=['Flu'])
print("P(Flu):\n", q1)

q2 = inference.query(variables=['Flu'], evidence={'Fever': 1})
print("\nP(Flu | Fever=True):\n", q2)

q3 = inference.query(variables=['Flu'], evidence={'Fever': 1, 'Cough': 1})
print("\nP(Flu | Fever=True, Cough=True):\n", q3)


'''
    return format_snippet(code)