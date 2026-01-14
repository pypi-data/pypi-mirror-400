"""
Flow Lab Functions for Knowledge Representation and Reasoning (KRR)
Complete lab code in single functions
"""


def flowlab6():
    """Complete Lab 6: Prolog Knowledge Base Tasks (Family, Access Control, Medical)"""
    from ._lab_code import LAB_CODE
    code = LAB_CODE.get(6, "Lab 6 code not found")
    print(code)


def flowlab7():
    """Complete Lab 7: Smart Hospital Semantic Network & Reasoning"""
    from ._lab_code import LAB_CODE
    code = LAB_CODE.get(7, "Lab 7 code not found")
    print(code)


def flowlab8():
    """Complete Lab 8: Fuzzy Logic and Fuzzy Reasoning"""
    from ._lab_code import LAB_CODE
    code = LAB_CODE.get(8, "Lab 8 code not found")
    print(code)


def flowlab11():
    """Complete Lab 11: Bayesian Networks and Probabilistic Reasoning"""
    from ._lab_code import LAB_CODE
    code = LAB_CODE.get(11, "Lab 11 code not found")
    print(code)


def flowlab12():
    """Complete Lab 12: Knowledge Representation with Bayesian Networks (pgmpy)"""
    from ._lab_code import LAB_CODE
    code = LAB_CODE.get(12, "Lab 12 code not found")
    print(code)


def flowoel2():
    """Complete OEL2: Prolog Knowledge Base - Role Hierarchy and Access Control"""
    from ._lab_code import LAB_CODE
    code = LAB_CODE.get('oel2', "OEL2 code not found")
    print(code)


def show_prolog_kb():
    """Show Prolog Knowledge Base - Role Hierarchy and Access Control (from OEL2)"""
    from ._lab_code import LAB_CODE
    code = LAB_CODE.get('oel2', "Prolog KB not found")
    print(code)


def flowtemplate():
    """Semantic Network Template - Complete solution template for exam questions"""
    from ._lab_code import LAB_CODE
    code = LAB_CODE.get('template', "Template not found")
    print(code)


def list_krr_labs():
    """List all available KRR lab functions"""
    labs = {
        6: "flowlab6() - Prolog Knowledge Base Tasks (Family, Access Control, Medical)",
        7: "flowlab7() - Smart Hospital Semantic Network & Reasoning",
        8: "flowlab8() - Fuzzy Logic & Fuzzy Reasoning",
        11: "flowlab11() - Bayesian Networks & Probabilistic Reasoning",
        12: "flowlab12() - Knowledge Representation (pgmpy)",
        'oel2': "flowoel2() - Prolog Knowledge Base (Role Hierarchy & Access Control)",
        'template': "flowtemplate() - Semantic Network Template (Exam Question Solution)"
    }
    print("\n" + "=" * 80)
    print("AVAILABLE KRR LAB FUNCTIONS")
    print("=" * 80)
    for lab_id, description in labs.items():
        if isinstance(lab_id, int):
            print(f"  Lab {lab_id:2}: {description}")
        else:
            print(f"  {lab_id.upper():>6}: {description}")
    print("=" * 80 + "\n")
