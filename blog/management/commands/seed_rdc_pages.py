from django.core.management.base import BaseCommand
from blog.models import Page, Menu, MenuItem


class Command(BaseCommand):
    help = "Seed modern, structured CMS pages and navigation menus for Rêves de Chiens"

    def handle(self, *args, **options):
        self.stdout.write("Seeding CMS pages for Rêves de Chiens...")

        pages_data = [
            {
                "title": "À propos de l'association",
                "slug": "a-propos",
                "seo_title": "À propos de l'association Rêves de Chiens",
                "seo_description": "Découvrez l'histoire, la mission et le fonctionnement 100% bénévole en Familles d'Accueil de l'association Rêves de Chiens.",
                "content": """
                <div class="cms-page-hero">
                    <p class="lead"><strong>Rêves de Chiens</strong> est une association de protection animale (loi 1901) à but non lucratif, animée par une équipe <strong>100% bénévole</strong>.</p>
                </div>

                <div class="cms-cards-grid" style="display:grid;grid-template-columns:repeat(auto-fit, minmax(260px, 1fr));gap:1.5rem;margin:2rem 0;">
                    <div style="background:#fdfaf6;padding:1.5rem;border-radius:12px;border:1px solid #fae1d6;">
                        <h3 style="color:#d45a30;margin-top:0;">🏡 100% Familles d'Accueil</h3>
                        <p>Nous ne disposons pas de refuge avec des cages. Tous nos animaux sauvés vivent au sein de <strong>Familles d'Accueil (FA)</strong> bienveillantes où ils sont soignés, sociabilisés et évalués en conditions réelles de vie de famille.</p>
                    </div>

                    <div style="background:#fdfaf6;padding:1.5rem;border-radius:12px;border:1px solid #fae1d6;">
                        <h3 style="color:#d45a30;margin-top:0;">🤝 100% Bénévoles</h3>
                        <p>Aucun salarié : chaque euro donné est intégralement dédié aux soins vétérinaires, à la nourriture et au bien-être de nos protégés. Nos équipes donnent de leur temps avec passion.</p>
                    </div>

                    <div style="background:#fdfaf6;padding:1.5rem;border-radius:12px;border:1px solid #fae1d6;">
                        <h3 style="color:#d45a30;margin-top:0;">📍 Notre Rayonnement</h3>
                        <p>Nous intervenons principalement en Île-de-France et départements limitrophes pour assurer le suivi, les pré-visites et l'accompagnement personnalisé de chaque adoption.</p>
                    </div>
                </div>

                <h2>Notre Mission au Quotidien</h2>
                <ul>
                    <li><strong>Sauver & Réhabiliter</strong> : Prise en charge d'animaux abandonnés, trouvés errants ou issus de situations de maltraitance.</li>
                    <li><strong>Soigner & Mettre en règle</strong> : Identification (puce électronique), vaccination complète, déparasitage et stérilisation obligatoire.</li>
                    <li><strong>Accompagner l'Adoption Responsable</strong> : Trouver le foyer idéal correspondant au caractère, aux besoins et au rythme de vie de chaque animal.</li>
                    <li><strong>Sensibiliser & Prévenir</strong> : Lutter contre les abandons et promouvoir la stérilisation ainsi que l'éducation positive.</li>
                </ul>
                """
            },
            {
                "title": "Conditions d'adoption",
                "slug": "conditions-adoption",
                "seo_title": "Conditions et démarches d'adoption - Rêves de Chiens",
                "seo_description": "Tout savoir sur les démarches, les frais et les engagements pour adopter un chien ou chat chez Rêves de Chiens.",
                "content": """
                <p class="lead">Adopter un animal est un engagement sur 10 à 15 ans. Pour garantir le bonheur de l'animal comme celui de votre famille, voici notre démarche en 4 étapes simples :</p>

                <div class="cms-steps" style="margin:2rem 0;">
                    <div style="display:flex;gap:1rem;margin-bottom:1.5rem;align-items:flex-start;">
                        <span style="background:#e8734a;color:#fff;width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:bold;flex-shrink:0;">1</span>
                        <div>
                            <h3 style="margin:0 0 0.5rem 0;">Formulaire & Prise de contact</h3>
                            <p>Vous repérez un protégé sur notre site et remplissez le questionnaire préalable envoyé par mail. Cela nous permet de vérifier la compatibilité initiale.</p>
                        </div>
                    </div>

                    <div style="display:flex;gap:1rem;margin-bottom:1.5rem;align-items:flex-start;">
                        <span style="background:#e8734a;color:#fff;width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:bold;flex-shrink:0;">2</span>
                        <div>
                            <h3 style="margin:0 0 0.5rem 0;">Échange téléphonique & Pré-visite</h3>
                            <p>Un bénévole échange avec vous pour répondre à toutes vos questions et réalise une pré-visite (physique ou visio) de votre domicile pour s'assurer de la sécurité de l'environnement.</p>
                        </div>
                    </div>

                    <div style="display:flex;gap:1rem;margin-bottom:1.5rem;align-items:flex-start;">
                        <span style="background:#e8734a;color:#fff;width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:bold;flex-shrink:0;">3</span>
                        <div>
                            <h3 style="margin:0 0 0.5rem 0;">Rencontre avec l'animal</h3>
                            <p>Rendez-vous dans la Famille d'Accueil de l'animal pour faire connaissance avec lui dans son environnement de vie quotidien.</p>
                        </div>
                    </div>

                    <div style="display:flex;gap:1rem;margin-bottom:1.5rem;align-items:flex-start;">
                        <span style="background:#e8734a;color:#fff;width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:bold;flex-shrink:0;">4</span>
                        <div>
                            <h3 style="margin:0 0 0.5rem 0;">Contrat & Certificat d'engagement</h3>
                            <p>Signature du contrat d'adoption, remise du carnet de santé, signature du certificat d'engagement et de connaissance (loi du 30 nov 2021) et participation aux frais vétérinaires.</p>
                        </div>
                    </div>
                </div>

                <h2>Frais d'adoption (Participation aux soins)</h2>
                <p>Nos frais d'adoption correspondent au remboursement partiel des actes vétérinaires réalisés systématiquement :</p>
                <ul>
                    <li><strong>Identification ICAD</strong> (puce électronique au nom de l'association puis transférée à l'adoptant)</li>
                    <li><strong>Vaccination complète</strong> (primo + rappel)</li>
                    <li><strong>Stérilisation / Castration</strong> obligatoire (ou bon de stérilisation pour les chiots/chatons trop jeunes)</li>
                    <li><strong>Déparasitage interne et externe</strong></li>
                </ul>
                """
            },
            {
                "title": "Conseils avant adoption",
                "slug": "conseils-adoption",
                "seo_title": "Conseils pratiques avant d'adopter - Rêves de Chiens",
                "seo_description": "Les questions essentielles à se poser et la checklist pour bien accueillir votre futur compagnon.",
                "content": """
                <p class="lead">Accueillir un animal dans son foyer transforme le quotidien. Pour que cette aventure soit une réussite totale, voici les points clés à anticiper :</p>

                <div style="background:#f8fafc;border-left:4px solid #3b82f6;padding:1.25rem;border-radius:0 8px 8px 0;margin:1.5rem 0;">
                    <h3 style="margin-top:0;color:#1e3a8a;">⏱ Le facteur Temps</h3>
                    <p>Un chien a besoin de balades quotidiennes d'au moins 1h à 1h30, quel que soit le temps extérieur. Un chat réclame des moments de jeu, d'attention et d'entretien de sa litière.</p>
                </div>

                <div style="background:#f8fafc;border-left:4px solid #10b981;padding:1.25rem;border-radius:0 8px 8px 0;margin:1.5rem 0;">
                    <h3 style="margin-top:0;color:#065f46;">💶 Le Budget Prévisionnel</h3>
                    <p>Au-delà de la participation à l'adoption, prévoyez un budget annuel (nourriture de qualité, antiparasitaires réguliers, vaccins annuels, mutuelle ou réserve en cas d'accident / maladie imprévue, garde pendant les vacances).</p>
                </div>

                <div style="background:#f8fafc;border-left:4px solid #f59e0b;padding:1.25rem;border-radius:0 8px 8px 0;margin:1.5rem 0;">
                    <h3 style="margin-top:0;color:#92400e;">🏡 La Checklist d'Accueil</h3>
                    <ul style="margin-bottom:0;">
                        <li>Un couchage douillet dans un endroit calme</li>
                        <li>Gamelles en inox ou céramique</li>
                        <li>Harnais physiologique et longe (pour chiens) / Bac à litière et griffoir (pour chats)</li>
                        <li>Patience et méthode d'éducation positive et bienveillante (la règle des 3 jours / 3 semaines / 3 mois d'adaptation)</li>
                    </ul>
                </div>
                """
            },
            {
                "title": "Conditions de prise en charge & Abandon",
                "slug": "conditions-abandon",
                "seo_title": "Prise en charge et abandon d'animal - Rêves de Chiens",
                "seo_description": "Procédure, conditions et informations importantes concernant les demandes de prise en charge par l'association.",
                "content": """
                <div style="background:#fef2f2;border:1px solid #fecaca;padding:1.5rem;border-radius:12px;margin-bottom:2rem;">
                    <h3 style="color:#991b1b;margin-top:0;">⚠️ Rappel fondamental</h3>
                    <p style="color:#7f1d1d;margin-bottom:0;">L'association <strong>Rêves de Chiens</strong> ne dispose <strong>d'aucun refuge physique</strong>. Tous nos sauvetages reposent sur des <strong>Familles d'Accueil bénévoles</strong>. Nos capacités d'accueil sont donc restreintes et réservées aux situations critiques sans autre solution.</p>
                </div>

                <h2>Procédure de Demande</h2>
                <ol>
                    <li><strong>Contact par formulaire / email</strong> : Sélectionnez le motif <em>"Demande de prise en charge / Abandon"</em> sur notre page de contact.</li>
                    <li><strong>Questionnaire d'évaluation</strong> : Vous recevrez par retour de mail notre questionnaire détaillé à renseigner impérativement avec photos et historique médical.</li>
                    <li><strong>Recherche d'une FA disponible</strong> : Si le dossier est recevable, nous sollicitons notre réseau de familles bénévoles compatibles.</li>
                </ol>

                <h2>Checklist préalable pour le propriétaire cédant</h2>
                <div style="background:#f8fafc;border:1px solid #e2e8f0;padding:1.25rem;border-radius:8px;margin:1.5rem 0;">
                    <p>Avant d'envisager une séparation définitive, assurez-vous d'avoir exploré ces démarches :</p>
                    <ul>
                        <li><strong>Bilan vétérinaire</strong> : Une douleur ou un problème hormonal peut expliquer un changement soudain de comportement.</li>
                        <li><strong>Éducateur / Comportementaliste</strong> : Avez-vous consulté un professionnel en méthodes positives ?</li>
                        <li><strong>Entourage</strong> : Des proches ou amis peuvent-ils vous épauler temporairement ?</li>
                    </ul>
                </div>

                <h2>Engagements et Frais</h2>
                <ul>
                    <li><strong>Frais de prise en charge</strong> : Une participation financière est demandée pour couvrir les frais de mise en règle sanitaire (vaccins, puce, stérilisation si non effectuée).</li>
                    <li><strong>Pas de pension temporaire</strong> : Toute prise en charge est définitive avec signature d'un acte officiel de cession au profit de l'association.</li>
                </ul>
                """
            },
            {
                "title": "Devenir Famille d'Accueil (FA)",
                "slug": "familles-accueil",
                "seo_title": "Devenir Famille d'Accueil pour animaux - Rêves de Chiens",
                "seo_description": "Ouvrez votre cœur et votre foyer : devenez Famille d'Accueil bénévole et sauvez des vies avec Rêves de Chiens.",
                "content": """
                <p class="lead">Les Familles d'Accueil sont le cœur battant de <strong>Rêves de Chiens</strong>. Sans elles, aucun sauvetage n'est possible !</p>

                <div style="background:#f0fdf4;border:1px solid #bbf7d0;padding:1.5rem;border-radius:12px;margin:1.5rem 0;">
                    <h3 style="color:#166534;margin-top:0;">💚 Quel est le rôle d'une FA ?</h3>
                    <p style="color:#14532d;">Accueillir temporairement un chien, un chat ou un rongeur chez vous, lui apporter tendresse, sécurité et stabilité, le temps qu'il trouve sa famille adoptive pour la vie.</p>
                </div>

                <h2>Les Avantages & Engagements de l'Association</h2>
                <ul>
                    <li><strong>Frais vétérinaires 100% pris en charge</strong> par Rêves de Chiens (consultations, chirurgies, médicaments).</li>
                    <li><strong>Fourniture du matériel si besoin</strong> (laisse, collier, harnais, panier, bac à litière).</li>
                    <li><strong>Accompagnement continu</strong> : Nos bénévoles référents sont disponibles 7j/7 pour vous conseiller et vous guider.</li>
                    <li><strong>Durée adaptée</strong> : Accueil d'urgence (quelques jours/semaines) ou accueil longue durée jusqu'à adoption.</li>
                </ul>

                <div style="text-align:center;margin:2.5rem 0;">
                    <a href="/contact/?category=fa" class="btn btn-primary btn-lg">🏡 Proposer ma candidature comme Famille d'Accueil</a>
                </div>
                """
            },
            {
                "title": "Dons, Parrainages & Partenaires",
                "slug": "dons-parrainages",
                "seo_title": "Faire un don ou parrainer un animal - Rêves de Chiens",
                "seo_description": "Soutenez les actions de l'association Rêves de Chiens : dons déductibles des impôts à 66%, Teaming, parrainages et partenaires.",
                "content": """
                <p class="lead">Votre générosité est indispensable pour soigner, nourrir et sauver nos animaux. Chaque don, même modeste, fait une immense différence.</p>

                <div class="donation-options" style="display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:1.5rem;margin:2rem 0;">
                    <div style="background:#ffffff;border:2px solid #e8734a;padding:1.5rem;border-radius:12px;text-align:center;box-shadow:0 4px 12px rgba(0,0,0,0.04);">
                        <h3 style="color:#e8734a;margin-top:0;">❤️ Don en ligne (HelloAsso)</h3>
                        <p>Don ponctuel ou mensuel sécurisé par carte bancaire. Reçu fiscal délivré immédiatement.</p>
                        <a href="https://www.helloasso.com" target="_blank" rel="noopener" class="btn btn-primary" style="display:inline-block;margin-top:1rem;">Faire un don sur HelloAsso</a>
                    </div>

                    <div style="background:#ffffff;border:2px solid #3b82f6;padding:1.5rem;border-radius:12px;text-align:center;box-shadow:0 4px 12px rgba(0,0,0,0.04);">
                        <h3 style="color:#3b82f6;margin-top:0;">🪙 Teaming (1€ / mois)</h3>
                        <p>Une micro-contribution solidaire de 1€ par mois pour soutenir nos factures vétérinaires.</p>
                        <a href="https://www.teaming.net" target="_blank" rel="noopener" class="btn btn-outline" style="display:inline-block;margin-top:1rem;">Rejoindre notre groupe Teaming</a>
                    </div>

                    <div style="background:#ffffff;border:2px solid #003087;padding:1.5rem;border-radius:12px;text-align:center;box-shadow:0 4px 12px rgba(0,0,0,0.04);">
                        <h3 style="color:#003087;margin-top:0;">💳 Don PayPal</h3>
                        <p>Effectuez un don direct et rapide via votre compte PayPal ou par carte.</p>
                        <a href="https://www.paypal.com" target="_blank" rel="noopener" class="btn btn-outline" style="display:inline-block;margin-top:1rem;">Donner avec PayPal</a>
                    </div>
                </div>

                <div style="background:#ecfdf5;border:1px solid #a7f3d0;padding:1.25rem;border-radius:12px;margin:2rem 0;">
                    <h3 style="color:#065f46;margin-top:0;">🧾 Déductibilité Fiscale de 66%</h3>
                    <p style="color:#064e3b;margin-bottom:0;">En tant qu'association d'intérêt général, vos dons ouvrent droit à une <strong>réduction d'impôt de 66%</strong> du montant versé (dans la limite de 20% du revenu imposable). <em>Un don de 50€ ne vous coûte réellement que 17€.</em></p>
                </div>

                <h2>Nos Partenaires & Soutiens</h2>
                <p>Un grand merci aux cliniques vétérinaires partenaires, aux donateurs réguliers et aux entreprises bienfaitrices qui nous permettent de poursuivre nos sauvetages chaque jour !</p>
                """
            },
            {
                "title": "Mentions légales & Transparence",
                "slug": "mentions-legales",
                "seo_title": "Mentions légales et transparence - Rêves de Chiens",
                "seo_description": "Informations juridiques, RNA, mentions hébergeur et transparence statutaire de l'association Rêves de Chiens.",
                "content": """
                <h2>1. Identification de l'Association</h2>
                <p><strong>Dénomination</strong> : Association Rêves de Chiens<br>
                <strong>Statut juridique</strong> : Association loi 1901 à but non lucratif<br>
                <strong>Numéro RNA</strong> : W751000000 (Enregistrée en Préfecture)<br>
                <strong>Siège social</strong> : 123 Rue du Refuge, 75001 Paris, France<br>
                <strong>Email</strong> : contact@revesdechiens.fr<br>
                <strong>Téléphone</strong> : 01 23 45 67 89</p>

                <h2>2. Direction & Responsable de Publication</h2>
                <p><strong>Président / Responsable de la publication</strong> : Le Conseil d'Administration de l'association Rêves de Chiens.</p>

                <h2>3. Hébergement du Site</h2>
                <p><strong>Hébergeur</strong> : Société d'hébergement sécurisé, conformité RGPD européenne.</p>

                <h2>4. Transparence Statutaire & Règlement Intérieur</h2>
                <p>Conformément à nos engagements de transparence et de gouvernance associative, les <strong>Statuts constitutifs</strong> et le <strong>Règlement intérieur</strong> de l'association sont consultables sur simple demande écrite adressée par email à <a href="mailto:contact@revesdechiens.fr">contact@revesdechiens.fr</a>.</p>

                <h2>5. Protection des Données Personnelles (RGPD)</h2>
                <p>Les informations recueillies via les formulaires de contact et d'adoption sont enregistrées dans un fichier informatisé sécurisé pour le traitement des candidatures. Elles ne sont jamais cédées, louées ni vendues à des tiers. Vous disposez d'un droit d'accès, de rectification et de suppression de vos données.</p>
                """
            },
            {
                "title": "Que sont-ils devenus ? (Les Adoptés)",
                "slug": "les-adoptes",
                "seo_title": "Que sont-ils devenus ? Les animaux adoptés de Rêves de Chiens",
                "seo_description": "Découvrez les nouvelles et photos de tous les chiens, chats et rongeurs adoptés grâce à l'association depuis 2011.",
                "content": """
                <div class="cms-page-hero">
                    <p class="lead">Depuis plus de 15 ans, grâce à votre soutien et au dévouement de nos familles d'accueil, des centaines d'animaux ont trouvé le bonheur dans un foyer pour la vie. Retrouvez ici leurs nouvelles et leurs visages épanouis !</p>
                </div>

                <div class="adoptees-year-selector" style="background:#f0f8fc;padding:1.25rem;border-radius:12px;border:1px solid #b8dfef;margin:2rem 0;">
                    <h3 style="margin-top:0;color:#2191C0;font-size:1.1rem;">🗓 Historique des Adoptions par Année :</h3>
                    <div style="display:flex;flex-wrap:wrap;gap:0.5rem;margin-top:0.75rem;">
                        <a href="#annee-2026" class="btn btn-sm btn-primary">2026</a>
                        <a href="#annee-2025" class="btn btn-sm btn-outline">2025</a>
                        <a href="#annee-2024" class="btn btn-sm btn-outline">2024</a>
                        <a href="#annee-2023" class="btn btn-sm btn-outline">2023</a>
                        <a href="#annee-2022" class="btn btn-sm btn-outline">2022</a>
                        <a href="#annee-2021" class="btn btn-sm btn-outline">2021</a>
                        <a href="#annee-2020" class="btn btn-sm btn-outline">2020</a>
                        <a href="#annee-2019" class="btn btn-sm btn-outline">2019</a>
                        <a href="#annee-2018" class="btn btn-sm btn-outline">2018</a>
                        <a href="#annee-2017" class="btn btn-sm btn-outline">2017</a>
                        <a href="#annee-2016" class="btn btn-sm btn-outline">2016</a>
                        <a href="#annee-2015" class="btn btn-sm btn-outline">2015</a>
                        <a href="#annee-2014" class="btn btn-sm btn-outline">2014</a>
                        <a href="#annee-2013" class="btn btn-sm btn-outline">2013</a>
                        <a href="#annee-2012" class="btn btn-sm btn-outline">2012</a>
                        <a href="#annee-2011" class="btn btn-sm btn-outline">2011</a>
                    </div>
                </div>

                <div id="annee-2026" style="margin-top:2.5rem;">
                    <h2 style="color:#2191C0;border-bottom:2px solid #e2e8f0;padding-bottom:0.5rem;">🎉 Les Heureux Adoptés de 2026</h2>
                    <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(260px, 1fr));gap:1.5rem;margin-top:1.5rem;">
                        <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;padding:1.25rem;box-shadow:0 2px 8px rgba(0,0,0,0.04);">
                            <h3 style="margin-top:0;color:#1e293b;">Verdi (Chat)</h3>
                            <p style="color:#64748b;font-size:0.9rem;"><em>Adopté en février 2026</em></p>
                            <p>Verdi passe désormais ses journées à ronronner sur son coussin au soleil dans sa nouvelle famille bienveillante.</p>
                        </div>
                        <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;padding:1.25rem;box-shadow:0 2px 8px rgba(0,0,0,0.04);">
                            <h3 style="margin-top:0;color:#1e293b;">Locky (Chien)</h3>
                            <p style="color:#64748b;font-size:0.9rem;"><em>Adopté en janvier 2026</em></p>
                            <p>Après plusieurs mois en FA, Locky a trouvé sa famille idéale avec un grand jardin et de longues balades en forêt.</p>
                        </div>
                        <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;padding:1.25rem;box-shadow:0 2px 8px rgba(0,0,0,0.04);">
                            <h3 style="margin-top:0;color:#1e293b;">Ulysse (Chiot)</h3>
                            <p style="color:#64748b;font-size:0.9rem;"><em>Adopté en janvier 2026</em></p>
                            <p>Ulysse grandit entouré d'amour et de jeux. Un sauvetage réussi grâce à la réactivité de nos bénévoles.</p>
                        </div>
                    </div>
                </div>

                <div style="text-align:center;margin-top:3rem;padding:2rem;background:#f8fafc;border-radius:12px;">
                    <h3>Vous avez adopté un animal chez Rêves de Chiens ?</h3>
                    <p>Envoyez-nous de ses nouvelles et des photos sur <a href="mailto:contact@revesdechiens.fr">contact@revesdechiens.fr</a> ou sur notre page <a href="https://www.instagram.com/refuge_reves_de_chiens/" target="_blank" rel="noopener">Instagram</a> !</p>
                </div>
                """
            },
        ]

        created_pages = {}
        for pdata in pages_data:
            page, created = Page.objects.update_or_create(
                slug=pdata["slug"],
                defaults={
                    "title": pdata["title"],
                    "content": pdata["content"],
                    "seo_title": pdata["seo_title"],
                    "seo_description": pdata["seo_description"],
                    "status": "published",
                }
            )
            created_pages[pdata["slug"]] = page
            action = "Created" if created else "Updated"
            self.stdout.write(f"  [{action}] Page: {page.title} (/{page.slug}/)")

        # Setup Menus
        self.stdout.write("Setting up Navigation Menus...")

        # 1. Main Header Menu
        main_menu, _ = Menu.objects.get_or_create(slug="main", defaults={"name": "Menu Principal"})
        main_menu.items.all().delete()
        MenuItem.objects.create(menu=main_menu, title="Accueil", url="/", position=1)
        MenuItem.objects.create(menu=main_menu, title="À l'adoption", url="/articles/", position=2)
        MenuItem.objects.create(menu=main_menu, title="L'association", linked_page=created_pages.get("a-propos"), position=3)
        MenuItem.objects.create(menu=main_menu, title="Conditions d'adoption", linked_page=created_pages.get("conditions-adoption"), position=4)
        MenuItem.objects.create(menu=main_menu, title="Familles d'Accueil", linked_page=created_pages.get("familles-accueil"), position=5)
        MenuItem.objects.create(menu=main_menu, title="Les Adoptés", linked_page=created_pages.get("les-adoptes"), position=6)
        MenuItem.objects.create(menu=main_menu, title="Dons & Parrainages", linked_page=created_pages.get("dons-parrainages"), position=7)
        MenuItem.objects.create(menu=main_menu, title="Contact", url="/contact/", position=8)

        # 2. Adoptions Sidebar Menu
        adoptions_menu, _ = Menu.objects.get_or_create(slug="adoptions", defaults={"name": "Adopter un animal"})
        adoptions_menu.items.all().delete()
        MenuItem.objects.create(menu=adoptions_menu, title="Tous nos protégés", url="/articles/", position=1)
        MenuItem.objects.create(menu=adoptions_menu, title="Nos chiens", url="/categorie/chiens/", position=2)
        MenuItem.objects.create(menu=adoptions_menu, title="Nos chats", url="/categorie/chats/", position=3)
        MenuItem.objects.create(menu=adoptions_menu, title="🚨 Recherche FA urgente", url="/categorie/urgences/", position=4)
        MenuItem.objects.create(menu=adoptions_menu, title="Conditions d'adoption", linked_page=created_pages.get("conditions-adoption"), position=5)
        MenuItem.objects.create(menu=adoptions_menu, title="Conseils d'accueil", linked_page=created_pages.get("conseils-adoption"), position=6)
        MenuItem.objects.create(menu=adoptions_menu, title="Que sont-ils devenus ? (Adoptés)", linked_page=created_pages.get("les-adoptes"), position=7)

        # 3. Plus d'infos Sidebar Menu
        plus_infos_menu, _ = Menu.objects.get_or_create(slug="plus_infos", defaults={"name": "En savoir plus"})
        plus_infos_menu.items.all().delete()
        MenuItem.objects.create(menu=plus_infos_menu, title="Qui sommes-nous ?", linked_page=created_pages.get("a-propos"), position=1)
        MenuItem.objects.create(menu=plus_infos_menu, title="Devenir Famille d'Accueil", linked_page=created_pages.get("familles-accueil"), position=2)
        MenuItem.objects.create(menu=plus_infos_menu, title="Conditions d'abandon & prise en charge", linked_page=created_pages.get("conditions-abandon"), position=3)
        MenuItem.objects.create(menu=plus_infos_menu, title="Faire un don / Parrainer", linked_page=created_pages.get("dons-parrainages"), position=4)
        MenuItem.objects.create(menu=plus_infos_menu, title="Que sont-ils devenus ?", linked_page=created_pages.get("les-adoptes"), position=5)
        MenuItem.objects.create(menu=plus_infos_menu, title="Mentions légales & Transparence", linked_page=created_pages.get("mentions-legales"), position=6)

        # 4. Footer Menu
        footer_menu, _ = Menu.objects.get_or_create(slug="footer", defaults={"name": "Menu Pied de Page"})
        footer_menu.items.all().delete()
        MenuItem.objects.create(menu=footer_menu, title="Accueil", url="/", position=1)
        MenuItem.objects.create(menu=footer_menu, title="À l'adoption", url="/articles/", position=2)
        MenuItem.objects.create(menu=footer_menu, title="L'association", linked_page=created_pages.get("a-propos"), position=3)
        MenuItem.objects.create(menu=footer_menu, title="Les Adoptés", linked_page=created_pages.get("les-adoptes"), position=4)
        MenuItem.objects.create(menu=footer_menu, title="Devenir FA", linked_page=created_pages.get("familles-accueil"), position=5)
        MenuItem.objects.create(menu=footer_menu, title="Dons & Soutiens", linked_page=created_pages.get("dons-parrainages"), position=6)
        MenuItem.objects.create(menu=footer_menu, title="Mentions légales", linked_page=created_pages.get("mentions-legales"), position=7)
        MenuItem.objects.create(menu=footer_menu, title="Contact", url="/contact/", position=8)

        self.stdout.write(self.style.SUCCESS("Successfully seeded all Rêves de Chiens CMS pages and dynamic menus!"))
