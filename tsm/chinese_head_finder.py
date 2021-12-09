from typing import List

from tsm.head_finder import AbstractCollinsHeadFinder


class ChineseHeadFinder(AbstractCollinsHeadFinder):

    def __init__(self):
        super().__init__()

        #If true, reverses the direction of search in VP and IP coordinations.
        # Works terribly .
        coord_switch: bool = False

        left_except_punct: List[str] = ["leftexcept", "PU"]
        right_except_punct: List[str] = ["rightexcept", "PU"]

        non_terminal_info = {}
        # these are first-cut rules

        left: str = "right" if coord_switch else "left"
        right: str = "left" if coord_switch else "right"
        rightdis: str = "rightdis"
        default_rule: List[str] = [right]

        # ROOT is not always unary for chinese -- PAIR is a special notation
        # that the Irish people use for non-unary ones....
        non_terminal_info["ROOT"] = [[left, "IP"]]
        non_terminal_info["PAIR"] = [[left, "IP"]]

        # Major syntactic categories
        non_terminal_info["ADJP"] = [[left, "JJ", "ADJP"]] # there is one ADJP unary rewrite to AD but otherwise all have JJ or ADJP
        non_terminal_info["ADVP"] = [[left, "AD", "CS", "ADVP", "JJ"]] # CS is a subordinating conjunctor, and there are a couple of ADVP->JJ unary rewrites
        non_terminal_info["CLP"] = [[right, "M", "CLP"]]
        non_terminal_info["CP"] = [[right, "DEC", "WHNP", "WHPP"], right_except_punct] # the (syntax-oriented) right-first head rule
        non_terminal_info["DNP"] = [[right, "DEG", "DEC"], right_except_punct] # according to tgrep2, first preparation, all DNPs have a DEG daughter
        non_terminal_info["DP"] = [[left, "DT", "DP"]] # there's one instance of DP adjunction
        non_terminal_info["DVP"] = [[right, "DEV", "DEC"]] # DVP always has DEV under it
        non_terminal_info["FRAG"] = [[right, "VV", "NN"], right_except_punct] # FRAG seems only to be used for bits at the beginnings of articles: "Xinwenshe<DATE>" and "(wan)"
        non_terminal_info["INTJ"] = [[right, "INTJ", "IJ", "SP"]]
        non_terminal_info["IP"] = [[left, "VP", "IP"], right_except_punct] # CDM July 2010 following email from Pi-Chuan changed preference to VP over IP: IP can be -SBJ, -OBJ, or -ADV, and shouldn't be head
        non_terminal_info["LCP"] = [[right, "LC", "LCP"]] # there's a bit of LCP adjunction
        non_terminal_info["LST"] = [[right, "CD", "PU"]] # covers all examples
        non_terminal_info["NP"] = [[right, "NN", "NR", "NT", "NP", "PN", "CP"]] # Basic heads are NN/NR/NT/NP; PN is pronoun.  Some NPs are nominalized relative clauses without overt nominal material; these are NP->CP unary rewrites.  Finally, note that this doesn't give any special treatment of coordination.
        non_terminal_info["PP"] = [[left, "P", "PP"]] # in the manual there's an example of VV heading PP but I couldn't find such an example with tgrep2
        # cdm 2006: PRN changed to not choose punctuation.  Helped parsing (if not significantly)
        non_terminal_info["PRN"] = [[left, "NP", "VP", "IP", "QP", "PP", "ADJP", "CLP", "LCP"], [rightdis, "NN", "NR", "NT", "FW"]]
        # cdm 2006: QP: add OD -- occurs some; occasionally NP, NT, M; parsing performance no-op
        non_terminal_info["QP"] = [[right, "QP", "CLP", "CD", "OD", "NP", "NT", "M"]] #there's some QP adjunction
        # add OD?
        non_terminal_info["UCP"] = [[left, ]] # an alternative would be "PU","CC"
        non_terminal_info["VP"] = [[left, "VP", "VCD", "VPT", "VV", "VCP", "VA", "VC", "VE", "IP", "VSB", "VCP", "VRD", "VNV"], left_except_punct] # note that ba and long bei introduce IP-OBJ small clauses; short bei introduces VP
        # add BA, LB, as needed

        # verb compounds
        non_terminal_info["VCD"] = [[left, "VCD", "VV", "VA", "VC", "VE"]] # could easily be right instead
        non_terminal_info["VCP"] = [[left, "VCD", "VV", "VA", "VC", "VE"]] # not much info from documentation
        non_terminal_info["VRD"] = [[left, "VCD", "VRD", "VV", "VA", "VC", "VE"]] # definitely left
        non_terminal_info["VSB"] = [[right, "VCD", "VSB", "VV", "VA", "VC", "VE"]] # definitely right, though some examples look questionably classified [na2lai2 zhi1fu4)
        non_terminal_info["VNV"] = [[left, "VV", "VA", "VC", "VE"]] # left/right doesn't matter
        non_terminal_info["VPT"] = [[left, "VV", "VA", "VC", "VE"]] # activity verb is to the left

        # some POS tags apparently sit where phrases are supposed to be
        non_terminal_info["CD"] = [[right, "CD"]]
        non_terminal_info["NN"] = [[right, "NN"]]
        non_terminal_info["NR"] = [[right, "NR"]]

        # I'm adding these POS tags to do primitive morphology for character-level
        # parsing.  It shouldn't affect anything else because heads of preterminals are not
        # generally queried - GMA
        non_terminal_info["VV"] = [[left]]
        non_terminal_info["VA"] = [[left]]
        non_terminal_info["VC"] = [[left]]
        non_terminal_info["VE"] = [[left]]

        # new for ctb6.
        non_terminal_info["FLR"] = [right_except_punct]

        # new for CTB9
        non_terminal_info["DFL"] = [right_except_punct]
        non_terminal_info["EMO"] = [left_except_punct] # left/right doesn't matter
        non_terminal_info["INC"] = [left_except_punct] 
        non_terminal_info["INTJ"] = [left_except_punct] 
        non_terminal_info["OTH"] = [left_except_punct] 
        non_terminal_info["SKIP"] = [left_except_punct] 