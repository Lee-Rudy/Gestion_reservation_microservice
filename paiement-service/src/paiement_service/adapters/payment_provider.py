"""
Adaptateur vers un fournisseur de paiement simulé (PSP).

Implémente le port IFournisseurPaiement sans aucun appel réseau.
Permet de développer et tester le service sans dépendance externe.

En production, remplacer cet adaptateur par une intégration réelle :
    - StripeAdapter      : via l'API Stripe
    - PaypalAdapter      : via l'API PayPal
    - AdyenAdapter       : via l'API Adyen
Le reste du code (domain + use cases) reste identique.
"""

from paiement_service.application.ports import IFournisseurPaiement
from paiement_service.domain.entities.paiement import Paiement


class FournisseurPaiementSimule(IFournisseurPaiement):
    """Simulateur de PSP configurable pour le développement et les tests.

    Le comportement (accepter ou refuser) est défini à l'instanciation,
    ce qui permet de tester facilement les deux branches (succès/échec).

    Exemple d'usage dans les tests :
        # PSP qui accepte tout
        fournisseur_ok = FournisseurPaiementSimule()

        # PSP qui refuse tout
        fournisseur_ko = FournisseurPaiementSimule(traitement_accepte=False)
    """

    def __init__(
        self,
        traitement_accepte: bool = True,
        remboursement_accepte: bool = True,
    ) -> None:
        """Configure le comportement du simulateur.

        Args:
            traitement_accepte: Si True, tous les paiements sont acceptés.
            remboursement_accepte: Si True, tous les remboursements sont acceptés.
        """
        self._traitement_accepte = traitement_accepte
        self._remboursement_accepte = remboursement_accepte

    def traiter(self, paiement: Paiement) -> bool:
        """Simule la soumission d'un paiement au PSP.

        En production : appel HTTP à l'API Stripe/PayPal avec les données
        de carte/compte et retour du résultat d'autorisation.

        Args:
            paiement: Le paiement à traiter (montant, devise, méthode).

        Returns:
            True si le PSP accepte, False s'il refuse.
        """
        # Simulation déterministe : résultat fixé à la construction
        return self._traitement_accepte

    def rembourser(self, paiement: Paiement) -> bool:
        """Simule une demande de remboursement auprès du PSP.

        En production : appel HTTP à l'API du PSP pour annuler
        ou créditer la transaction d'origine.

        Args:
            paiement: Le paiement précédemment validé à rembourser.

        Returns:
            True si le remboursement est accepté, False sinon.
        """
        # Simulation déterministe : résultat fixé à la construction
        return self._remboursement_accepte
