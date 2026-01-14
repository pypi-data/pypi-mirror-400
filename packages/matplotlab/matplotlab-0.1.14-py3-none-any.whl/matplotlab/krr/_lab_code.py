"""
KRR Lab Code - Embedded Complete Notebook Code and Prolog
==========================================================

This module contains the complete code from all KRR lab notebooks,
embedded as string constants for easy access via flowlab functions.

Lab 6: Prolog Knowledge Base Tasks (Family, Access Control, Medical)
Lab 7: Smart Hospital Semantic Network & Reasoning
Lab 8: Fuzzy Logic and Fuzzy Reasoning
Lab 11: Bayesian Networks and Probabilistic Reasoning
Lab 12: Knowledge Representation with Prolog (Original)
OEL2: Fuzzy Logic and Prolog Knowledge Base
"""

LAB_CODE = {
    6: '''parent(john, mary).
parent(john, alex).
parent(mary, susan).
parent(alex, lila).
parent(alex, omar).
parent(david, sam).
parent(sofia, sam).

male(john).
male(alex).
male(david).
male(sam).
male(omar).

female(mary).
female(susan).
female(lila).
female(sofia).

mother(X, Y) :- parent(X, Y), female(X).
father(X, Y) :- parent(X, Y), male(X).
sibling(X, Y) :- parent(Z, X), parent(Z, Y), Y \\= X.
uncle(X, Y) :- parent(Z, Y), sibling(Z, X), male(X).
aunt(X, Y) :- parent(Z, Y), sibling(Z, X), female(X).
grandparent(X, Y) :- parent(X, Z), parent(Z, Y).
ancestor(X, Y) :- parent(X, Y).
ancestor(X, Z) :- parent(X, Y), ancestor(Y, Z).

role(alice, admin).
role(sara, manager).
role(bob, staff).
role(hamza, intern).

resource(payroll).
resource(report).

read_allowed(User, Resource) :- role(User, admin), resource(Resource).
read_allowed(User, Resource) :- role(User, manager), resource(Resource).
read_allowed(User, report) :- role(User, staff), resource(report).
read_allowed(User, report) :- role(User, intern), resource(report).

write_allowed(User, Resource) :- role(User, admin), resource(Resource).
write_allowed(User, payroll) :- role(User, staff), resource(payroll).

patient(ahmed).
patient(noor).
patient(sami).

showing_symptom(ahmed, fever).
showing_symptom(ahmed, cough).
showing_symptom(ahmed, headache).
showing_symptom(noor, fever).
showing_symptom(sami, fever).
showing_symptom(sami, cough).

likely_flu(Patient) :- patient(Patient), showing_symptom(Patient, fever), showing_symptom(Patient, cough).
needs_rest(Patient) :- patient(Patient), likely_flu(Patient).
needs_checkup(Patient) :- patient(Patient), showing_symptom(Patient, fever).
needs_checkup(Patient) :- patient(Patient), showing_symptom(Patient, headache).
checkup_then_rest(Patient) :- patient(Patient), needs_rest(Patient), needs_checkup(Patient).''',

    7: '''class(staff).
class(doctor).
class(nurse).
class(robot_nurse).

is_a(doctor, staff).
is_a(nurse, staff).
is_a(robot_nurse, nurse).

instance_of(alice, doctor).
instance_of(bob, nurse).
instance_of(rx1, robot_nurse).

has_property(staff, human, global).
has_property(nurse, assists_in_surgery, global).
has_property(robot_nurse, human, global_false).
has_property(robot_nurse, autonomous, global).
has_property(doctor, on_call, context(emergency_mode)).
has_property(doctor, off_duty, context(normal_mode)).
has_property(robot_nurse, active, time(day_shift)).
has_property(robot_nurse, inactive, time(night_shift)).

has_property(C, P) :- has_property(C, P, global).

subclass_of(C, C).
subclass_of(Sub, Super) :- is_a(Sub, Mid), subclass_of(Mid, Super).

is_member_of(Instance, Class) :- instance_of(Instance, C0), subclass_of(C0, Class).

instance_property(Instance, Prop) :- instance_of(Instance, C0), class_property(C0, Prop).

class_property(Class, Prop) :- has_property(Class, Prop, global).
class_property(Class, Prop) :- is_a(Class, Super), class_property(Super, Prop).

effective_property(X, Prop, context(Ctx)) :- has_property(X, Prop, context(Ctx)).
effective_property(X, Prop, context(Ctx)) :- instance_of(X, C0), has_property(C0, Prop, context(Ctx)).
effective_property(X, Prop, context(Ctx)) :- instance_of(X, C0), is_a(C0, Super), has_property(Super, Prop, context(Ctx)).

effective_property(X, Prop, time(T)) :- has_property(X, Prop, time(T)).
effective_property(X, Prop, time(T)) :- instance_of(X, C0), has_property(C0, Prop, time(T)).
effective_property(X, Prop, time(T)) :- instance_of(X, C0), is_a(C0, Super), has_property(Super, Prop, time(T)).

explain_membership(Inst, Super, [instance_of(Inst, C0)|Path]) :- instance_of(Inst, C0), explain_up(C0, Super, Path).

explain_up(C, C, []).
explain_up(C, Super, [is_a(C, P)|Path]) :- is_a(C, P), explain_up(P, Super, Path).''',

    8: '''# ==============
# Smart Room Temperature Advisor (Fuzzy Logic)
# KRR Lab Python version (for Google Colab)
# ============================================

# 1) Generic Membership Functions
def tri(a, b, c, x):
    """Triangular membership function. a <= b <= c"""
    if x <= a or x >= c:
        return 0.0
    elif a < x <= b:
        return (x - a) / (b - a)
    else: # b < x < c
        return (c - x) / (c - b)

def trap(a, b, c, d, x):
    """Trapezoidal membership function. a <= b <= c <= d"""
    if x <= a or x >= d:
        return 0.0
    elif b <= x <= c:
        return 1.0
    elif a < x < b:
        return (x - a) / (b - a)
    else: # c < x < d
        return (d - x) / (d - c)

# 2) Fuzzy Sets for Temperature and Fan Speed
# You can change these ranges if you want.

def mu_temp_cold(t):
    # Cold around 0-18°C
    return trap(0, 0, 10, 18, t)

def mu_temp_warm(t):
    # Warm around 15-28°C
    return tri(15, 22, 28, t)

def mu_temp_hot(t):
    # Hot around 25-40°C
    return trap(25, 30, 40, 40, t)

def mu_fan_off(s):
    # Off (low speed, 0-35)
    return trap(0, 0, 20, 35, s)

def mu_fan_medium(s):
    # Medium (around 30-70)
    return tri(30, 50, 70, s)

def mu_fan_high(s):
    # High (around 60-100)
    return trap(60, 80, 100, 100, s)

# 3) Fuzzy Operators
def fuzzy_and(a, b):
    return min(a, b)

def fuzzy_or(a, b):
    return max(a, b)

# 4) Rule Base
# Rules:
# 1. IF temperature is cold -> fan = off
# 2. IF temperature is warm -> fan = medium
# 3. IF temperature is hot -> fan = high

def fuzzify_temperature(t):
    """Returns a dict with membership values for each temperature label."""
    return {
        "cold": mu_temp_cold(t),
        "warm": mu_temp_warm(t),
        "hot": mu_temp_hot(t),
    }

def apply_rules(temp_mfs):
    """Apply the rules and return rule strengths."""
    # Since each rule has ONE antecedent, rule strength is that membership.
    rule_strengths = {}
    # Rule 1: IF temp is cold THEN fan = off
    rule_strengths["R1_cold_to_off"] = temp_mfs["cold"]
    # Rule 2: IF temp is warm THEN fan = medium
    rule_strengths["R2_warm_to_medium"] = temp_mfs["warm"]
    # Rule 3: IF temp is hot THEN fan = high
    rule_strengths["R3_hot_to_high"] = temp_mfs["hot"]
    
    return rule_strengths

# 5) Aggregation + Defuzzification (Mamdani, centroid method)
def aggregate_and_defuzzify(rule_strengths, step=1.0):
    """Aggregate the consequents and defuzzify to get crisp fan speed."""
    # Universe of discourse for fan speed
    # 0 completely off, 100 maximum speed
    xs = [x for x in range(0, 101, int(step))]
    aggregated_mu = []
    
    for s in xs:
        # Individual consequents
        mu_off = mu_fan_off(s)
        mu_medium = mu_fan_medium(s)
        mu_high = mu_fan_high(s)
        
        # "clip" each consequent by its rule strength (Mamdani)
        r1 = fuzzy_and(rule_strengths["R1_cold_to_off"], mu_off)
        r2 = fuzzy_and(rule_strengths["R2_warm_to_medium"], mu_medium)
        r3 = fuzzy_and(rule_strengths["R3_hot_to_high"], mu_high)
        
        # aggregated output membership at speed s (max of all rules)
        mu_agg = max(r1, r2, r3)
        aggregated_mu.append(mu_agg)
        
    # Centroid defuzzification: sum(x * mu(x)) / sum(mu(x))
    numerator = 0.0
    denominator = 0.0
    
    for x, mu in zip(xs, aggregated_mu):
        numerator += x * mu
        denominator += mu
        
    if denominator == 0:
        crisp_speed = 0.0 # no activation at all
    else:
        crisp_speed = numerator / denominator
        
    return crisp_speed

def classify_fan_label(crisp_speed):
    """Given the defuzzified fan speed, classify it into off/medium/high."""
    mu_off = mu_fan_off(crisp_speed)
    mu_medium = mu_fan_medium(crisp_speed)
    mu_high = mu_fan_high(crisp_speed)
    
    labels = {
        "off": mu_off,
        "medium": mu_medium,
        "high": mu_high
    }
    
    # Pick the label with maximum membership
    best_label = max(labels, key=labels.get)
    return best_label, labels

# 6) Main interaction
def run_smart_room_advisor():
    print("=== Smart Room Temperature Advisor (Fuzzy) ===")
    try:
        temp = float(input("Enter current room temperature (°C): "))
    except ValueError:
        print("Invalid input. Please enter a numeric value.")
        return
        
    # Step 1: Fuzzify temperature
    temp_mfs = fuzzify_temperature(temp)
    print("\\n--- Temperature Membership Values ---")
    print(f"µ_cold({temp}) = {temp_mfs['cold']:.3f}")
    print(f"µ_warm({temp}) = {temp_mfs['warm']:.3f}")
    print(f"µ_hot({temp}) = {temp_mfs['hot']:.3f}")
    
    # Step 2: Apply rules
    rule_strengths = apply_rules(temp_mfs)
    print("\\n--- Rule Strengths (Firing Levels) ---")
    print(f"R1: IF temp is cold THEN fan = off -> strength = {rule_strengths['R1_cold_to_off']:.3f}")
    print(f"R2: IF temp is warm THEN fan = medium -> strength = {rule_strengths['R2_warm_to_medium']:.3f}")
    print(f"R3: IF temp is hot THEN fan = high -> strength = {rule_strengths['R3_hot_to_high']:.3f}")
    
    # Step 3: Aggregate & defuzzify
    crisp_speed = aggregate_and_defuzzify(rule_strengths, step=1.0)
    
    # Step 4: Classify final label
    label, label_mfs = classify_fan_label(crisp_speed)
    
    print("\\n--- Final Fan Speed Decision ---")
    print(f"Crisp fan speed (0-100): {crisp_speed:.2f}")
    print(f"Fan speed linguistic label: {label.upper()}")
    
    print("\\nMembership of crisp speed in output sets:")
    print(f"µ_off({crisp_speed:.2f}) = {label_mfs['off']:.3f}")
    print(f"µ_medium({crisp_speed:.2f}) = {label_mfs['medium']:.3f}")
    print(f"µ_high({crisp_speed:.2f}) = {label_mfs['high']:.3f}")
    print("\\n==========================================\\n")


if __name__ == "__main__":
    run_smart_room_advisor()''',

    11: '''# ============================================================
# Lab: Modeling Uncertainty with Bayesian Networks
# ============================================================

# Scenario 1 - Smart Health Diagnosis Assistant
# ---------------------------------------------

# Prior probability of Flu: P(Flu)
P_Flu = {
    True: 0.1,  # 10% base chance of flu
    False: 0.9
}

# Conditional probability of Fever given Flu: P(Fever | Flu)
P_Fever_given_Flu = {
    True: {True: 0.8, False: 0.2},
    False: {True: 0.2, False: 0.8}
}

# Conditional probability of Cough given Flu: P(Cough | Flu)
P_Cough_given_Flu = {
    True: {True: 0.7, False: 0.3},
    False: {True: 0.3, False: 0.7}
}

def joint_probability(fever, cough, flu):
    """Compute joint probability P(Fever, Cough, Flu)"""
    p_flu = P_Flu[flu]
    p_fever_given_flu = P_Fever_given_Flu[flu][fever]
    p_cough_given_flu = P_Cough_given_Flu[flu][cough]
    return p_flu * p_fever_given_flu * p_cough_given_flu

def evidence_probability(fever=None, cough=None):
    """Compute P(evidence) by summing over Flu=[True, False]"""
    total = 0.0
    for flu in [True, False]:
        for f_val in [True, False]:
            for c_val in [True, False]:
                # Check if this combination matches the evidence
                if fever is not None and f_val != fever:
                    continue
                if cough is not None and c_val != cough:
                    continue
                total += joint_probability(f_val, c_val, flu)
    return total

def posterior_flu(fever=None, cough=None):
    """Compute P(Flu=True | evidence) using Bayes' Rule"""
    # Numerator: sum over all combinations consistent with evidence where Flu=True
    num = 0.0
    for f_val in [True, False]:
        for c_val in [True, False]:
            if fever is not None and f_val != fever:
                continue
            if cough is not None and c_val != cough:
                continue
            num += joint_probability(f_val, c_val, True)
            
    den = evidence_probability(fever=fever, cough=cough)
    if den == 0:
        return 0.0
    return num / den

print("Functions for Scenario 1 defined.")

# Queries for Scenario 1
p_flu_given_fever = posterior_flu(fever=True)
print(f"P(Flu | Fever=True) = {p_flu_given_fever:.4f}")

p_flu_given_fever_cough = posterior_flu(fever=True, cough=True)
print(f"P(Flu | Fever=True, Cough=True) = {p_flu_given_fever_cough:.4f}")

print(f"Base rate P(Flu=True) = {P_Flu[True]:.4f}")


# Scenario 2 - Smart Car Fault Detection
# ---------------------------------------------

# Prior probability for LowOil
P_LowOil = {
    True: 0.2,  # 20% of the time, oil level is low
    False: 0.8
}

# P(EngineFailure | LowOil)
P_EngineFailure_given_LowOil = {
    True: {True: 0.6, False: 0.4},
    False: {True: 0.1, False: 0.9}
}

# P(EngineLight | EngineFailure)
P_EngineLight_given_EngineFailure = {
    True: {True: 0.9, False: 0.1},
    False: {True: 0.2, False: 0.8}
}

def joint_prob_car(low_oil, engine_failure, engine_light):
    """Compute P(LowOil, EngineFailure, EngineLight)"""
    p_low = P_LowOil[low_oil]
    p_fail_given_low = P_EngineFailure_given_LowOil[low_oil][engine_failure]
    p_light_given_fail = P_EngineLight_given_EngineFailure[engine_failure][engine_light]
    return p_low * p_fail_given_low * p_light_given_fail

def evidence_prob_car(engine_light=None, low_oil=None):
    """Compute P(evidence) by summing over all hidden states"""
    total = 0.0
    for lo in [True, False]:
        for ef in [True, False]:
            for el in [True, False]:
                if engine_light is not None and el != engine_light:
                    continue
                if low_oil is not None and lo != low_oil:
                    continue
                total += joint_prob_car(lo, ef, el)
    return total

def posterior_engine_failure(engine_light=None, low_oil=None):
    """Compute P(EngineFailure=True | evidence)"""
    num = 0.0
    for lo in [True, False]:
        for el in [True, False]:
            if engine_light is not None and el != engine_light:
                continue
            if low_oil is not None and lo != low_oil:
                continue
            num += joint_prob_car(lo, True, el)
            
    den = evidence_prob_car(engine_light=engine_light, low_oil=low_oil)
    if den == 0:
        return 0.0
    return num / den

print("Functions for Scenario 2 defined.")

# Queries for Scenario 2
p_fail_given_light = posterior_engine_failure(engine_light=True)
print(f"P(EngineFailure | EngineLight=True) = {p_fail_given_light:.4f}")

p_fail_given_light_low = posterior_engine_failure(engine_light=True, low_oil=True)
print(f"P(EngineFailure | EngineLight=True, LowOil=True) = {p_fail_given_light_low:.4f}")''',

    12: '''# ============================================================================
# Lab 12: Knowledge Representation with Bayesian Networks (pgmpy)
# ============================================================================

# This uses pgmpy library for structured Bayesian Network modeling
# from KRR_LAB_12_NOTEBOOK.ipynb

# Task 1: Basic Bayesian Network
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination

model = DiscreteBayesianNetwork([
    ('Flu', 'Fever'),
    ('Flu', 'Cough'),
    ('Flu', 'TestResult')
])

cpd_flu = TabularCPD(variable='Flu', variable_card=2, values=[[0.9], [0.1]])

cpd_fever = TabularCPD(variable='Fever', variable_card=2,
                       values=[[0.8, 0.2],
                               [0.2, 0.8]],
                       evidence=['Flu'], evidence_card=[2])

cpd_cough = TabularCPD(variable='Cough', variable_card=2,
                       values=[[0.7, 0.3],
                               [0.3, 0.7]],
                       evidence=['Flu'], evidence_card=[2])

cpd_test = TabularCPD(variable='TestResult', variable_card=2,
                      values=[[0.9, 0.05],
                              [0.1, 0.95]],
                      evidence=['Flu'], evidence_card=[2])

model.add_cpds(cpd_flu, cpd_fever, cpd_cough, cpd_test)
model.check_model()

infer = VariableElimination(model)

print("--- PART B: Inference ---")
print("1. P(Flu):")
print(infer.query(variables=['Flu']))

print("\\n2. P(Flu | Fever=True):")
print(infer.query(variables=['Flu'], evidence={'Fever': 1}))

print("\\n3. P(Flu | Fever=True, Cough=True):")
print(infer.query(variables=['Flu'], evidence={'Fever': 1, 'Cough': 1}))

print("\\n4. P(TestResult=Positive | Flu=True):")
print(infer.query(variables=['TestResult'], evidence={'Flu': 1}))

print("\\n--- PART C: What-If Reasoning ---")
print("1. P(Flu | Cough=False, Fever=True):")
print(infer.query(variables=['Flu'], evidence={'Cough': 0, 'Fever': 1}))

print("\\n2. P(Flu | TestResult=Positive, Fever=False):")
print(infer.query(variables=['Flu'], evidence={'TestResult': 1, 'Fever': 0}))

# Task 2: Spam Detection Network
spam_model = DiscreteBayesianNetwork([
    ('SenderReputation', 'Spam'),
    ('Spam', 'ContainsLinks'),
    ('Spam', 'SuspiciousWords')
])

cpd_reputation = TabularCPD(variable='SenderReputation', variable_card=2, values=[[0.2], [0.8]])

cpd_spam = TabularCPD(variable='Spam', variable_card=2,
                      values=[[0.9, 0.1],
                              [0.1, 0.9]],
                      evidence=['SenderReputation'], evidence_card=[2])

cpd_links = TabularCPD(variable='ContainsLinks', variable_card=2,
                       values=[[0.8, 0.2],
                               [0.2, 0.8]],
                       evidence=['Spam'], evidence_card=[2])

cpd_words = TabularCPD(variable='SuspiciousWords', variable_card=2,
                       values=[[0.9, 0.4],
                               [0.1, 0.6]],
                       evidence=['Spam'], evidence_card=[2])

spam_model.add_cpds(cpd_reputation, cpd_spam, cpd_links, cpd_words)
spam_model.check_model()

spam_infer = VariableElimination(spam_model)

print("\\n--- Post-Lab Inference ---")
print("1. P(Spam):")
print(spam_infer.query(variables=['Spam']))

print("\\n2. P(Spam | ContainsLinks=True):")
print(spam_infer.query(variables=['Spam'], evidence={'ContainsLinks': 1}))

print("\\n3. P(Spam | ContainsLinks=True, SenderReputation=Good):")
print(spam_infer.query(variables=['Spam'], evidence={'ContainsLinks': 1, 'SenderReputation': 1}))''',

    'oel2': '''% ============================================================================
% PROLOG KNOWLEDGE BASE - Role Hierarchy and Access Control (from KRR_OEL2)
% ============================================================================

% Role hierarchy
is_a(student, person).
is_a(staff, person).

is_a(ta, student).
is_a(ta, staff).

is_a(lecturer, staff).
is_a(lab_admin, staff).

% Instances
instance_of(ali, student).
instance_of(sana, ta).
instance_of(sohail, ta).
instance_of(hamza, lecturer).
instance_of(dr_faize, lab_admin).
instance_of(maroof, staff).

% Context
context(normal_day).
context(exam_day).

% Restrictions and duties
restricted(maroof).
on_duty(sohail, exam_day).

% Inheritance-aware role lookup
has_role(Person, Role):- instance_of(Person, Role).
has_role(Person, Role):- instance_of(Person, R), is_a(R, Role).
has_role(Person, Role):- instance_of(Person, R), is_a(R, Parent), is_a(Parent, Role).

% Restriction override
can_enter(Person, _, deny):- restricted(Person).

% Normal day rules
can_enter(Person, normal_day, allow):- has_role(Person, staff).
can_enter(Person, normal_day, deny):- has_role(Person, student), \\+ has_role(Person, staff).

% Exam day rules
can_enter(Person, exam_day, allow):- has_role(Person, lecturer).
can_enter(Person, exam_day, allow):- has_role(Person, lab_admin).
can_enter(Person, exam_day, allow):- has_role(Person, ta), on_duty(Person, exam_day).
can_enter(Person, exam_day, deny):- has_role(Person, student), \\+ has_role(Person, ta).

decision(Person, Context, Decision):- can_enter(Person, Context, Decision).
''',

    'template': '''% ============================================================================
% SEMANTIC NETWORK TEMPLATE - Simple & Ready to Customize
% ============================================================================
% EXAMPLE: University Department System
% Copy this, change the domain/entities, save as .pl file, and run!
% ============================================================================

% === STEP 1: CLASS HIERARCHY ===
is_a(lecturer, employee).
is_a(student, person).
is_a(ta, student).

% === STEP 2: INSTANCES ===
instance_of(dr_smith, lecturer).
instance_of(john, student).
instance_of(alice, ta).

% === STEP 3: PROPERTIES & RELATIONSHIPS ===
property(dr_smith, department, cs).
property(john, major, cs).
property(alice, year, 2).

relationship(dr_smith, teaches, cs101).
relationship(john, enrolls_in, cs101).
relationship(alice, assists, cs101).

% === STEP 4: INHERITANCE & RULES ===
has_class(X, Class) :- instance_of(X, Class).
has_class(X, Class) :- instance_of(X, C), is_a(C, Class).

get_property(X, P, V) :- property(X, P, V).

% === STEP 5: INFERENCE RULES ===
is_employee(X) :- has_class(X, employee).
is_teacher(X) :- has_class(X, lecturer).
takes_course(X, C) :- relationship(X, enrolls_in, C).

% === STEP 6: TEST QUERIES ===
% Run in SWI-Prolog:
% ?- instance_of(john, student).
% ?- has_class(alice, student).
% ?- property(dr_smith, department, X).
% ?- relationship(john, enrolls_in, C).
% ?- is_employee(dr_smith).
% ?- takes_course(john, cs101).

% ============================================================================
% HOW TO USE THIS TEMPLATE:
% ============================================================================
% 1. Copy everything above
% 2. Change domain name (e.g., "Hospital System")
% 3. Replace class names (e.g., doctor, patient, nurse)
% 4. Replace instances (e.g., dr_ahmed, patient_001)
% 5. Add your properties and relationships
% 6. Add your inference rules
% 7. Save as: my_solution.pl
% 8. Run: ?- consult('my_solution.pl').
% 9. Test: ?- your_query.
% ============================================================================
'''
}
