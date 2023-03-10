# Classe permettant de récupérer une chaine de caractères du sommaire de wikipédia
# Au final, on obtiendra soit l'intégralité du sommaire, soit les grands titres (équivalents à un h2 html)
class Navigation_sommaire_wikipedia:
    def __init__(self, sections, choix_section):
        self.sections = sections
        self.choix_section = choix_section
        self.sommaire = ""

    def print_sections_h2(self, sections, level=0):
        liste_reduite_sommaire_h2 = []
        for s in sections:
            liste_reduite_sommaire_h2.append(s.title)
        return liste_reduite_sommaire_h2

    def print_sections_complet(self, sections, level=0):
        liste_complete_sommaire = []
        for s in sections:
            liste_complete_sommaire.append(s.title)
            self.print_sections_complet(s.sections)
        return liste_complete_sommaire

    def nav_wiki(self):
        sommaire = ""
        try:
            if self.choix_section == "sommaire":
                sommaire = self.print_sections_complet(self.sections)
            elif self.choix_section == "section":
                sommaire = self.print_sections_h2(self.sections)
            else:
                print(
                    "Erreur dans le fonctionnement de la classe Navigation_sommaire_wikipedia.")
        except Exception as err:
            print(f"Unexpected {err}, {type(err)}")
        sommaire = "".join(str(sommaire))
        self.sommaire = sommaire


# exemple:
# 1) test = Navigation_wikipedia(page_py.sections,section_traitee)
# 2) test.nav_wiki()
# 3) test.sommaire
