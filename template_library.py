#!/usr/bin/env python3
"""
Legal Document Template Library

Provides Belgian legal document templates including motions, contracts,
legal letters, and citation formats. Supports both Dutch and French.
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path


class TemplateLibrary:
    """
    Library of Belgian legal document templates.
    """
    
    def __init__(self):
        """Initialize the template library with Belgian legal templates."""
        self.templates = self._load_belgian_templates()
        self.template_categories = {
            "motions": "Rechtszaken en Procedures",
            "contracts": "Contracten en Overeenkomsten",
            "letters": "Juridische Brieven",
            "citations": "Citatieformaten",
            "clauses": "Contractclausules",
            "forms": "Formulieren"
        }
    
    def _load_belgian_templates(self) -> Dict[str, Any]:
        """Load Belgian legal document templates."""
        return {
            "motions": {
                "dagvaarding": {
                    "name": "Dagvaarding",
                    "description": "Dagvaarding voor de rechtbank van eerste aanleg",
                    "language": "nl",
                    "jurisdiction": "federaal",
                    "template": """DAGVAARDING

In naam van de Koning,

De ondergetekende, {advocaat_naam}, advocaat te {plaats}, kantoorhoudend te {adres}, 
dagvaardt {gedaagde_naam}, wonende te {gedaagde_adres}, om te verschijnen voor de 
{rechtbank_naam} te {rechtbank_plaats}, op {datum} om {tijd} uur, ter terechtzitting 
van de {afdeling} afdeling, om te horen uitspraak doen in de zaak van {eiser_naam}, 
wonende te {eiser_adres}, tegen {gedaagde_naam}.

VORDERINGEN:
{specifieke_vorderingen}

GRONDEN:
{gronden}

De ondergetekende verzoekt de rechtbank om de gedaagde te veroordelen tot het 
betalen van de proceskosten.

{plaats}, {datum}

{advocaat_naam}
Advocaat
{adres}""",
                    "variables": [
                        "advocaat_naam", "plaats", "adres", "gedaagde_naam", 
                        "gedaagde_adres", "rechtbank_naam", "rechtbank_plaats", 
                        "datum", "tijd", "afdeling", "eiser_naam", "eiser_adres",
                        "specifieke_vorderingen", "gronden"
                    ]
                },
                "conclusie": {
                    "name": "Conclusie",
                    "description": "Conclusie tot vordering",
                    "language": "nl",
                    "jurisdiction": "federaal",
                    "template": """CONCLUSIE TOT VORDERING

In de zaak van {eiser_naam}, wonende te {eiser_adres}, 
tegen {gedaagde_naam}, wonende te {gedaagde_adres}.

De ondergetekende, {advocaat_naam}, advocaat van {eiser_naam}, 
concludeert tot het volgende:

VORDERINGEN:
{specifieke_vorderingen}

GRONDEN:
{gronden}

De ondergetekende verzoekt de rechtbank om de gedaagde te veroordelen tot het 
betalen van de proceskosten.

{plaats}, {datum}

{advocaat_naam}
Advocaat
{adres}""",
                    "variables": [
                        "eiser_naam", "eiser_adres", "gedaagde_naam", "gedaagde_adres",
                        "advocaat_naam", "specifieke_vorderingen", "gronden", 
                        "plaats", "datum", "adres"
                    ]
                },
                "requete": {
                    "name": "Requête",
                    "description": "Requête pour le tribunal de première instance",
                    "language": "fr",
                    "jurisdiction": "federaal",
                    "template": """REQUÊTE

Au nom du Roi,

Le soussigné, {avocat_nom}, avocat à {lieu}, exerçant à {adresse}, 
cite {defendeur_nom}, demeurant à {defendeur_adresse}, à comparaître devant le 
{tribunal_nom} à {tribunal_lieu}, le {date} à {heure} heures, à l'audience de la 
{section} section, pour entendre statuer sur l'affaire de {demandeur_nom}, 
demeurant à {demandeur_adresse}, contre {defendeur_nom}.

DEMANDES:
{demandes_specifiques}

MOYENS:
{moyens}

Le soussigné prie le tribunal de condamner le défendeur aux dépens.

{lieu}, le {date}

{avocat_nom}
Avocat
{adresse}""",
                    "variables": [
                        "avocat_nom", "lieu", "adresse", "defendeur_nom",
                        "defendeur_adresse", "tribunal_nom", "tribunal_lieu",
                        "date", "heure", "section", "demandeur_nom", "demandeur_adresse",
                        "demandes_specifiques", "moyens"
                    ]
                }
            },
            "contracts": {
                "arbeidsovereenkomst": {
                    "name": "Arbeidsovereenkomst",
                    "description": "Model arbeidsovereenkomst voor onbepaalde tijd",
                    "language": "nl",
                    "jurisdiction": "federaal",
                    "template": """ARBEIDSOVEREENKOMST VOOR ONBEPAALDE TIJD

Tussen:
{werkgever_naam}, gevestigd te {werkgever_adres}, hierna te noemen "de werkgever",
en
{werknemer_naam}, wonende te {werknemer_adres}, hierna te noemen "de werknemer",

Wordt de volgende arbeidsovereenkomst gesloten:

ARTIKEL 1 - FUNCTIE
De werknemer wordt aangesteld als {functie} en zal werkzaam zijn op de afdeling {afdeling}.

ARTIKEL 2 - PLAATS VAN TEWERKSTELLING
De werknemer zal werkzaam zijn te {werkplaats}.

ARTIKEL 3 - ARBEIDSVOORWAARDEN
3.1. De werknemer ontvangt een brutoloon van €{brutoloon} per maand.
3.2. Het loon wordt maandelijks uitbetaald op de {loondatum} van elke maand.
3.3. De werknemer heeft recht op {vakantiedagen} vakantiedagen per jaar.

ARTIKEL 4 - WERKTIJDEN
De normale werkweek bedraagt {werkuren} uren, verdeeld over {werkdagen} werkdagen.

ARTIKEL 5 - PROEFTIJDPERIODE
Deze overeenkomst wordt aangegaan voor een proeftijd van {proeftijd} maanden.

ARTIKEL 6 - OPZEGGING
De opzeggingstermijn bedraagt {opzegtermijn} maanden.

{plaats}, {datum}

Werkgever: {werkgever_naam}
Werknemer: {werknemer_naam}""",
                    "variables": [
                        "werkgever_naam", "werkgever_adres", "werknemer_naam", 
                        "werknemer_adres", "functie", "afdeling", "werkplaats",
                        "brutoloon", "loondatum", "vakantiedagen", "werkuren",
                        "werkdagen", "proeftijd", "opzegtermijn", "plaats", "datum"
                    ]
                },
                "huurovereenkomst": {
                    "name": "Huurovereenkomst",
                    "description": "Model huurovereenkomst voor woonruimte",
                    "language": "nl",
                    "jurisdiction": "federaal",
                    "template": """HUUROVEREENKOMST WOONRUIMTE

Tussen:
{verhuurder_naam}, wonende te {verhuurder_adres}, hierna te noemen "de verhuurder",
en
{huurder_naam}, wonende te {huurder_adres}, hierna te noemen "de huurder",

Wordt de volgende huurovereenkomst gesloten voor de huur van:
{gehuurde_ruimte}

ARTIKEL 1 - HUURPRIJS
De huurprijs bedraagt €{huurprijs} per maand, te betalen vooruit op de {betaaldatum} van elke maand.

ARTIKEL 2 - WAARBORG
De huurder stort een waarborg van €{waarborg} op rekening {waarborg_rekening}.

ARTIKEL 3 - DUUR
Deze huurovereenkomst wordt aangegaan voor een periode van {huurperiode} jaar.

ARTIKEL 4 - VERPLICHTINGEN
4.1. De verhuurder is verplicht de gehuurde ruimte in goede staat te onderhouden.
4.2. De huurder is verplicht de gehuurde ruimte netjes te houden en te gebruiken.

{plaats}, {datum}

Verhuurder: {verhuurder_naam}
Huurder: {huurder_naam}""",
                    "variables": [
                        "verhuurder_naam", "verhuurder_adres", "huurder_naam",
                        "huurder_adres", "gehuurde_ruimte", "huurprijs", "betaaldatum",
                        "waarborg", "waarborg_rekening", "huurperiode", "plaats", "datum"
                    ]
                }
            },
            "letters": {
                "ingebrekestelling": {
                    "name": "Ingebrekestelling",
                    "description": "Formele ingebrekestelling",
                    "language": "nl",
                    "jurisdiction": "federaal",
                    "template": """INGEBREKESTELLING

{datum}

{ontvanger_naam}
{ontvanger_adres}

Betreft: Ingebrekestelling

Geachte {ontvanger_titel},

Namens mijn cliënt, {cliënt_naam}, vestig ik uw aandacht op het volgende:

{feiten}

Deze situatie is in strijd met {rechtsgrond}.

Ik stel u hiermee in gebreke en verzoek u om binnen {termijn} dagen na ontvangst van 
deze brief de volgende maatregelen te treffen:

{gevraagde_maatregelen}

Indien u niet binnen deze termijn aan mijn verzoek voldoet, zal ik genoodzaakt zijn 
om verdere juridische stappen te ondernemen, waaronder het instellen van een 
rechtszaak, zonder verdere waarschuwing.

Hoogachtend,

{advocaat_naam}
Advocaat
{advocaat_adres}""",
                    "variables": [
                        "datum", "ontvanger_naam", "ontvanger_adres", "ontvanger_titel",
                        "cliënt_naam", "feiten", "rechtsgrond", "termijn", 
                        "gevraagde_maatregelen", "advocaat_naam", "advocaat_adres"
                    ]
                },
                "mise_en_demeure": {
                    "name": "Mise en demeure",
                    "description": "Mise en demeure formelle",
                    "language": "fr",
                    "jurisdiction": "federaal",
                    "template": """MISE EN DEMEURE

{date}

{destinataire_nom}
{destinataire_adresse}

Objet: Mise en demeure

Monsieur/Madame {destinataire_titre},

Au nom de mon client, {client_nom}, je porte à votre attention ce qui suit:

{faits}

Cette situation est contraire à {base_juridique}.

Je vous mets en demeure et vous demande de prendre les mesures suivantes dans 
les {délai} jours suivant la réception de cette lettre:

{mesures_demandées}

Si vous ne répondez pas à ma demande dans ce délai, je serai contraint de prendre 
d'autres mesures juridiques, y compris l'engagement d'une procédure judiciaire, 
sans autre avertissement.

Cordialement,

{avocat_nom}
Avocat
{avocat_adresse}""",
                    "variables": [
                        "date", "destinataire_nom", "destinataire_adresse", 
                        "destinataire_titre", "client_nom", "faits", "base_juridique",
                        "délai", "mesures_demandées", "avocat_nom", "avocat_adresse"
                    ]
                }
            },
            "citations": {
                "belgische_citatie": {
                    "name": "Belgische Citatie",
                    "description": "Standaard citatieformaat voor Belgische rechtspraak",
                    "language": "nl",
                    "jurisdiction": "federaal",
                    "template": """{rechtbank}, {datum}, {zaaknummer}, {rechtsleer}""",
                    "variables": ["rechtbank", "datum", "zaaknummer", "rechtsleer"]
                },
                "european_citation": {
                    "name": "European Citation",
                    "description": "Standard citation format for European case law",
                    "language": "en",
                    "jurisdiction": "eu",
                    "template": """{court}, {date}, Case {case_number}, {legal_doctrine}""",
                    "variables": ["court", "date", "case_number", "legal_doctrine"]
                }
            },
            "clauses": {
                "geheimhouding": {
                    "name": "Geheimhoudingsclausule",
                    "description": "Standaard geheimhoudingsclausule",
                    "language": "nl",
                    "jurisdiction": "federaal",
                    "template": """ARTIKEL {artikelnummer} - GEHEIMHOUDING

{partij_naam} verbindt zich ertoe alle vertrouwelijke informatie die zij in het 
kader van deze overeenkomst ontvangt, strikt geheim te houden en niet aan derden 
te verstrekken zonder voorafgaande schriftelijke toestemming van {andere_partij}.

Deze geheimhoudingsverplichting blijft van kracht gedurende {duur} jaar na 
beëindiging van deze overeenkomst.""",
                    "variables": ["artikelnummer", "partij_naam", "andere_partij", "duur"]
                },
                "force_majeure": {
                    "name": "Force Majeure Clause",
                    "description": "Standard force majeure clause",
                    "language": "en",
                    "jurisdiction": "federaal",
                    "template": """ARTICLE {article_number} - FORCE MAJEURE

Neither party shall be liable for any failure or delay in performance under this 
agreement due to circumstances beyond its reasonable control, including but not 
limited to acts of God, war, terrorism, riots, fire, natural disasters, or 
government actions.

In the event of force majeure, the affected party shall notify the other party 
promptly and use reasonable efforts to resume performance as soon as possible.""",
                    "variables": ["article_number"]
                }
            },
            "forms": {
                "klacht_formulier": {
                    "name": "Klachtformulier",
                    "description": "Standaard klachtformulier",
                    "language": "nl",
                    "jurisdiction": "federaal",
                    "template": """KLACHTFORMULIER

Persoonlijke gegevens:
Naam: {klager_naam}
Adres: {klager_adres}
Telefoon: {klager_telefoon}
E-mail: {klager_email}

Beschrijving van de klacht:
{klacht_beschrijving}

Gewenste oplossing:
{gewenste_oplossing}

Datum: {datum}
Handtekening: {handtekening}""",
                    "variables": [
                        "klager_naam", "klager_adres", "klager_telefoon", 
                        "klager_email", "klacht_beschrijving", "gewenste_oplossing",
                        "datum", "handtekening"
                    ]
                }
            }
        }
    
    def get_template(self, category: str, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific template by category and ID.
        
        Args:
            category: Template category
            template_id: Template identifier
            
        Returns:
            Template dictionary or None if not found
        """
        return self.templates.get(category, {}).get(template_id)
    
    def list_templates(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        List available templates.
        
        Args:
            category: Optional category filter
            
        Returns:
            Dictionary of templates
        """
        if category:
            return {category: self.templates.get(category, {})}
        return self.templates
    
    def search_templates(self, query: str) -> List[Dict[str, Any]]:
        """
        Search templates by name or description.
        
        Args:
            query: Search query
            
        Returns:
            List of matching templates
        """
        results = []
        query_lower = query.lower()
        
        for category, templates in self.templates.items():
            for template_id, template in templates.items():
                if (query_lower in template['name'].lower() or 
                    query_lower in template['description'].lower()):
                    results.append({
                        'category': category,
                        'template_id': template_id,
                        'template': template
                    })
        
        return results
    
    def get_templates_by_language(self, language: str) -> List[Dict[str, Any]]:
        """
        Get templates by language.
        
        Args:
            language: Language code (nl, fr, en)
            
        Returns:
            List of templates in specified language
        """
        results = []
        
        for category, templates in self.templates.items():
            for template_id, template in templates.items():
                if template.get('language') == language:
                    results.append({
                        'category': category,
                        'template_id': template_id,
                        'template': template
                    })
        
        return results
    
    def get_templates_by_jurisdiction(self, jurisdiction: str) -> List[Dict[str, Any]]:
        """
        Get templates by jurisdiction.
        
        Args:
            jurisdiction: Jurisdiction code
            
        Returns:
            List of templates for specified jurisdiction
        """
        results = []
        
        for category, templates in self.templates.items():
            for template_id, template in templates.items():
                if template.get('jurisdiction') == jurisdiction:
                    results.append({
                        'category': category,
                        'template_id': template_id,
                        'template': template
                    })
        
        return results
    
    def get_template_categories(self) -> Dict[str, str]:
        """
        Get template categories with descriptions.
        
        Returns:
            Dictionary of categories and descriptions
        """
        return self.template_categories
    
    def validate_template_variables(self, template_id: str, category: str, 
                                  variables: Dict[str, str]) -> Dict[str, Any]:
        """
        Validate template variables.
        
        Args:
            template_id: Template identifier
            category: Template category
            variables: Provided variables
            
        Returns:
            Validation result with missing and extra variables
        """
        template = self.get_template(category, template_id)
        if not template:
            return {'valid': False, 'error': 'Template not found'}
        
        required_vars = set(template.get('variables', []))
        provided_vars = set(variables.keys())
        
        missing_vars = required_vars - provided_vars
        extra_vars = provided_vars - required_vars
        
        return {
            'valid': len(missing_vars) == 0,
            'missing_variables': list(missing_vars),
            'extra_variables': list(extra_vars),
            'required_variables': list(required_vars)
        } 