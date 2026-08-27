from django.core.management.base import BaseCommand
from blog.models import Page, Menu, MenuItem, Category, Redirect, AdoptionTariff


class Command(BaseCommand):
    help = "Seed modern, structured CMS pages, adoption tariffs, and navigation menus for Rêves de Chiens"

    def handle(self, *args, **options):
        self.stdout.write("Seeding CMS pages, Tarifs & Menus for Rêves de Chiens...")

        # 1. Clean up obsolete seeds & configure redirections
        self.stdout.write("Cleaning up obsolete pages & setting up redirections...")
        Page.objects.filter(slug="les-adoptes").delete()
        Page.objects.filter(slug="conseils-adoption").delete()

        Redirect.objects.update_or_create(
            old_path="/conseils-adoption/",
            defaults={
                "new_path": "/puis-je-adopter/",
                "is_permanent": True,
            }
        )

        # 2. Seed Adoption Tariffs (Tarifs 2026 administrables)
        self.stdout.write("Seeding Adoption Tariffs (2026)...")
        tariffs_data = [
            # Chiens
            {"species": "chien", "age_bracket": "Jusqu'à 11 mois", "amount": 350.00, "order": 1, "notes": "Chiot : primo + rappel, puce ICAD, vermifuge, bon de stérilisation"},
            {"species": "chien", "age_bracket": "De 1 à 5 ans", "amount": 270.00, "order": 2, "notes": "Chien adulte : vacciné, identifié, stérilisé, déparasité"},
            {"species": "chien", "age_bracket": "Plus de 6 ans", "amount": 130.00, "order": 3, "notes": "Chien senior : participation réduite, bilan vétérinaire"},
            # Chats
            {"species": "chat", "age_bracket": "Jusqu'à 6 mois", "amount": 195.00, "order": 1, "notes": "Chaton : Typhus-Coryza, leucose, puce, déparasitage, bon de stérilisation"},
            {"species": "chat", "age_bracket": "De 7 mois à 9 ans", "amount": 150.00, "order": 2, "notes": "Chat adulte : test FIV/FeLV, vacciné, identifié, stérilisé"},
            {"species": "chat", "age_bracket": "Plus de 10 ans", "amount": 80.00, "order": 3, "notes": "Chat senior / Panier retraite"},
        ]

        for tdata in tariffs_data:
            tariff, _ = AdoptionTariff.objects.update_or_create(
                species=tdata["species"],
                age_bracket=tdata["age_bracket"],
                defaults={
                    "amount": tdata["amount"],
                    "order": tdata["order"],
                    "notes": tdata["notes"],
                    "is_active": True,
                }
            )
            self.stdout.write(f"  [Tarif] {tariff.get_species_display()} - {tariff.age_bracket} : {tariff.amount} €")

        # 3. Seed CMS Pages
        self.stdout.write("Seeding CMS Pages...")
        pages_data = [
            # Page 1: Puis-je adopter ?
            {
                "title": "Puis-je adopter ?",
                "slug": "puis-je-adopter",
                "seo_title": "Puis-je adopter ? Les bonnes questions avant de vous engager - Rêves de Chiens",
                "seo_description": "Avant d'adopter un animal, posez-vous les bonnes questions sur le temps, le budget, le mode de vie et découvrez les atouts d'un animal adulte.",
                "content": """
                <div class="cms-page-hero" style="background:linear-gradient(135deg, #eef7fc 0%, #ffffff 100%);padding:2rem;border-radius:16px;border:1px solid #d0e7f7;margin-bottom:2.5rem;">
                    <h2 style="color:#1982c4;margin-top:0;font-size:1.6rem;">Avant d'adopter un animal : les bonnes questions à se poser</h2>
                    <p class="lead" style="margin-bottom:0;color:#2d3748;font-size:1.1rem;line-height:1.6;">
                        Adopter un animal est une décision importante qui demande mûre réflexion. Avant de vous engager pour de nombreuses années, prenez le temps de vous poser les questions essentielles ci-dessous.
                    </p>
                </div>

                <div class="cms-questions-grid" style="display:grid;grid-template-columns:repeat(auto-fit, minmax(300px, 1fr));gap:1.5rem;margin-bottom:3rem;">
                    <div style="background:#ffffff;padding:1.5rem;border-radius:14px;border:1px solid #e2e8f0;box-shadow:0 4px 12px rgba(0,0,0,0.03);">
                        <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.75rem;">
                            <span style="display:inline-flex;width:32px;height:32px;border-radius:50%;background:#1982c4;color:#fff;font-weight:bold;align-items:center;justify-content:center;font-size:0.9rem;">1</span>
                            <h3 style="margin:0;font-size:1.15rem;color:#1e293b;">Ai-je suffisamment de temps à lui consacrer ?</h3>
                        </div>
                        <p style="color:#475569;margin-bottom:0.75rem;">Un animal a besoin d'attention, de présence et de soins quotidiens. Pour un chien, cela implique notamment :</p>
                        <ul style="color:#475569;margin-bottom:0.5rem;padding-left:1.25rem;">
                            <li>Plusieurs promenades par jour (au moins 3 à 4, et pas seulement quelques minutes) ;</li>
                            <li>Du temps pour le jeu, l'éducation et les interactions ;</li>
                            <li>Un entretien régulier (brossage, bains, soins divers).</li>
                        </ul>
                        <p style="color:#1982c4;font-size:0.9rem;font-weight:600;margin-top:0.5rem;margin-bottom:0;">🐾 Un chiot demande encore davantage de disponibilité, particulièrement durant ses premiers mois.</p>
                    </div>

                    <div style="background:#ffffff;padding:1.5rem;border-radius:14px;border:1px solid #e2e8f0;box-shadow:0 4px 12px rgba(0,0,0,0.03);">
                        <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.75rem;">
                            <span style="display:inline-flex;width:32px;height:32px;border-radius:50%;background:#1982c4;color:#fff;font-weight:bold;align-items:center;justify-content:center;font-size:0.9rem;">2</span>
                            <h3 style="margin:0;font-size:1.15rem;color:#1e293b;">Mon mode de vie est-il compatible ?</h3>
                        </div>
                        <p style="color:#475569;margin-bottom:0.75rem;">Votre activité professionnelle et votre emploi du temps vous permettent-ils de répondre pleinement à ses besoins physiologiques et affectifs ?</p>
                        <p style="color:#475569;margin-bottom:0;">Un chien ou un chat peut vivre <strong>plus de 15 ans</strong>. Cette adoption représente donc un engagement fort sur le très long terme.</p>
                    </div>

                    <div style="background:#ffffff;padding:1.5rem;border-radius:14px;border:1px solid #e2e8f0;box-shadow:0 4px 12px rgba(0,0,0,0.03);">
                        <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.75rem;">
                            <span style="display:inline-flex;width:32px;height:32px;border-radius:50%;background:#1982c4;color:#fff;font-weight:bold;align-items:center;justify-content:center;font-size:0.9rem;">3</span>
                            <h3 style="margin:0;font-size:1.15rem;color:#1e293b;">Ai-je les moyens financiers nécessaires ?</h3>
                        </div>
                        <p style="color:#475569;margin-bottom:0.75rem;">Un animal engendre des dépenses régulières incompressibles :</p>
                        <ul style="color:#475569;margin-bottom:0.5rem;padding-left:1.25rem;">
                            <li>Alimentation adaptée à son âge, sa taille et ses besoins ;</li>
                            <li>Soins vétérinaires, vaccins et rappels annuels ;</li>
                            <li>Traitements antiparasitaires et vermifuges ;</li>
                            <li>Accessoires (panier, laisse, collier, harnais, jouets...) ;</li>
                            <li>Toilettage régulier pour certaines races.</li>
                        </ul>
                    </div>

                    <div style="background:#ffffff;padding:1.5rem;border-radius:14px;border:1px solid #e2e8f0;box-shadow:0 4px 12px rgba(0,0,0,0.03);">
                        <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.75rem;">
                            <span style="display:inline-flex;width:32px;height:32px;border-radius:50%;background:#1982c4;color:#fff;font-weight:bold;align-items:center;justify-content:center;font-size:0.9rem;">4</span>
                            <h3 style="margin:0;font-size:1.15rem;color:#1e293b;">Comment m'organiser pendant les vacances ?</h3>
                        </div>
                        <p style="color:#475569;margin-bottom:0.75rem;">Avant toute adoption, réfléchissez dès maintenant aux solutions envisageables :</p>
                        <ul style="color:#475569;margin-bottom:0.5rem;padding-left:1.25rem;">
                            <li>Emmener votre animal avec vous (hébergements acceptant les animaux) ;</li>
                            <li>Le confier à un proche de confiance ;</li>
                            <li>Recourir à une pension professionnelle ou à un pet-sitter certifié.</li>
                        </ul>
                    </div>

                    <div style="background:#ffffff;padding:1.5rem;border-radius:14px;border:1px solid #e2e8f0;box-shadow:0 4px 12px rgba(0,0,0,0.03);">
                        <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.75rem;">
                            <span style="display:inline-flex;width:32px;height:32px;border-radius:50%;background:#1982c4;color:#fff;font-weight:bold;align-items:center;justify-content:center;font-size:0.9rem;">5</span>
                            <h3 style="margin:0;font-size:1.15rem;color:#1e293b;">Suis-je prêt à faire face aux imprévus ?</h3>
                        </div>
                        <p style="color:#475569;margin-bottom:0;">Comme tout être vivant, un animal peut tomber malade, subir un accident, développer une allergie ou nécessiter des soins chirurgicaux coûteux. Ces situations demandent du temps, de l'organisation et un budget de sécurité.</p>
                    </div>

                    <div style="background:#ffffff;padding:1.5rem;border-radius:14px;border:1px solid #e2e8f0;box-shadow:0 4px 12px rgba(0,0,0,0.03);">
                        <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.75rem;">
                            <span style="display:inline-flex;width:32px;height:32px;border-radius:50%;background:#1982c4;color:#fff;font-weight:bold;align-items:center;justify-content:center;font-size:0.9rem;">6</span>
                            <h3 style="margin:0;font-size:1.15rem;color:#1e293b;">Suis-je prêt à l'accueillir correctement ?</h3>
                        </div>
                        <p style="color:#475569;margin-bottom:0.75rem;">L'arrivée dans un nouveau foyer représente un grand bouleversement pour lui. Durant les premiers jours, il peut être désorienté ou stressé : patience et compréhension sont indispensables.</p>
                        <p style="color:#475569;margin-bottom:0;"><strong>À préparer avant son arrivée :</strong> nourriture adaptée, gamelles, couchage douillet, laisse et collier/harnais, jouets et accessoires.</p>
                    </div>

                    <div style="background:#ffffff;padding:1.5rem;border-radius:14px;border:1px solid #e2e8f0;box-shadow:0 4px 12px rgba(0,0,0,0.03);grid-column:1 / -1;">
                        <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.75rem;">
                            <span style="display:inline-flex;width:32px;height:32px;border-radius:50%;background:#1982c4;color:#fff;font-weight:bold;align-items:center;justify-content:center;font-size:0.9rem;">7</span>
                            <h3 style="margin:0;font-size:1.15rem;color:#1e293b;">Que se passerait-il si je ne pouvais plus m'en occuper ?</h3>
                        </div>
                        <p style="color:#475569;margin-bottom:0;">Il est également essentiel d'anticiper l'avenir : en cas d'accident, d'incapacité prolongée ou de décès du propriétaire, il est impératif d'avoir convenu d'une solution de relais auprès d'un proche ou d'un héritier pour lui éviter un placement traumatisant en fourrière ou en refuge.</p>
                    </div>
                </div>

                <!-- Callout Engagement -->
                <div style="background:#fef3c7;border-left:5px solid #f59e0b;padding:1.75rem;border-radius:0 14px 14px 0;margin:2.5rem 0;">
                    <h3 style="margin-top:0;color:#92400e;display:flex;align-items:center;gap:8px;">
                        <span>❤️</span> Un engagement pour la vie
                    </h3>
                    <p style="color:#78350f;margin-bottom:0;font-size:1.05rem;line-height:1.6;">
                        L'adoption doit être envisagée comme un engagement à long terme. Si votre situation actuelle est trop instable ou incertaine, il est préférable de reporter votre projet jusqu'au moment où vous pourrez accueillir un compagnon dans les meilleures conditions.
                    </p>
                </div>

                <!-- Section Animal Adulte -->
                <div style="margin-top:3.5rem;">
                    <h2 style="color:#1982c4;font-size:1.6rem;margin-bottom:1.5rem;">Pourquoi adopter un animal adulte ?</h2>

                    <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:1.5rem;">
                        <div style="background:#f8fafc;border:1px solid #cbd5e1;padding:1.5rem;border-radius:12px;">
                            <h3 style="color:#0f172a;margin-top:0;font-size:1.1rem;">1. Il est déjà éduqué</h3>
                            <p style="color:#475569;margin-bottom:0;">Particulièrement pour les chiens : vous évitez l'apprentissage de la propreté, les mordillements, les destructions de meubles, les aboiements intempestifs et la phase délicate de l'adolescence. Une solution parfaite si vous manquez de temps ou d'expérience.</p>
                        </div>

                        <div style="background:#f8fafc;border:1px solid #cbd5e1;padding:1.5rem;border-radius:12px;">
                            <h3 style="color:#0f172a;margin-top:0;font-size:1.1rem;">2. Son état de santé est connu</h3>
                            <p style="color:#475569;margin-bottom:0;">Nos protégés bénéficient d'un suivi vétérinaire complet : vaccinés, identifiés par puce, stérilisés ou castrés, vermifugés et traités contre les parasites. Tout éventuel problème de santé vous est transparentement précisé, avec carnet de santé à jour.</p>
                        </div>

                        <div style="background:#f8fafc;border:1px solid #cbd5e1;padding:1.5rem;border-radius:12px;">
                            <h3 style="color:#0f172a;margin-top:0;font-size:1.1rem;">3. Son coût d'adoption est plus faible</h3>
                            <p style="color:#475569;margin-bottom:0;">La participation financière demandée couvre principalement les soins vétérinaires déjà réalisés. Vous n'avez pas à avancer les premiers soins onéreux indispensables aux chiots et chatons.</p>
                        </div>

                        <div style="background:#f8fafc;border:1px solid #cbd5e1;padding:1.5rem;border-radius:12px;">
                            <h3 style="color:#0f172a;margin-top:0;font-size:1.1rem;">4. Son caractère est déjà connu</h3>
                            <p style="color:#475569;margin-bottom:0;">À partir d'un an pour un chien et 6 mois pour un chat, sa personnalité est affirmée (calme, joueur, affectueux, indépendant, sociable). Grâce à nos <strong>Familles d'Accueil</strong>, son comportement en situation réelle est parfaitement documenté.</p>
                        </div>

                        <div style="background:#f8fafc;border:1px solid #cbd5e1;padding:1.5rem;border-radius:12px;grid-column:1 / -1;">
                            <h3 style="color:#0f172a;margin-top:0;font-size:1.1rem;">5. Vous lui offrez une seconde chance</h3>
                            <p style="color:#475569;margin-bottom:0;">De nombreux chiens et chats se retrouvent abandonnés sans faute de leur part. En adoptant un adulte, vous lui permettez de retrouver un foyer chaleureux. Malgré leur passé, ils développent un attachement d'une fidélité extraordinaire avec leurs adoptants.</p>
                        </div>
                    </div>
                </div>

                <div style="text-align:center;margin-top:3rem;">
                    <a href="/conditions-adoption/" class="btn btn-primary btn-lg" style="margin-right:1rem;">Découvrir les conditions d'adoption &rarr;</a>
                    <a href="/articles/" class="btn btn-outline btn-lg">Voir tous nos protégés à l'adoption</a>
                </div>
                """
            },

            # Page 2: Conditions d'adoption et tarifs
            {
                "title": "Conditions d'adoption et tarifs",
                "slug": "conditions-adoption",
                "seo_title": "Conditions d'adoption, démarches et tarifs 2026 - Rêves de Chiens",
                "seo_description": "Découvrez les étapes de l'adoption (premier contact, pré-adoption 3 semaines, adoption définitive), les pièces à fournir et la grille des tarifs 2026.",
                "content": """
                <div class="cms-page-hero" style="background:linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%);padding:2rem;border-radius:16px;border:1px solid #bbf7d0;margin-bottom:2.5rem;">
                    <h2 style="color:#166534;margin-top:0;font-size:1.6rem;">Les étapes d'une adoption responsable</h2>
                    <p class="lead" style="margin-bottom:0;color:#14532d;font-size:1.1rem;line-height:1.6;">
                        Chez <strong>Rêves de Chiens</strong>, chaque adoption est encadrée avec bienveillance pour garantir le bonheur durable de l'animal et de sa nouvelle famille.
                    </p>
                </div>

                <!-- 3 Étapes -->
                <div class="cms-adoption-steps" style="display:flex;flex-direction:column;gap:1.75rem;margin-bottom:3rem;">
                    <!-- Étape 1 -->
                    <div style="background:#ffffff;border:1px solid #e2e8f0;padding:1.75rem;border-radius:14px;box-shadow:0 4px 12px rgba(0,0,0,0.03);">
                        <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem;">
                            <span style="background:#1982c4;color:#fff;font-weight:800;font-size:1.1rem;width:40px;height:40px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;flex-shrink:0;">1</span>
                            <h3 style="margin:0;color:#0f172a;font-size:1.3rem;">Étape 1 : Premier contact & Rencontre</h3>
                        </div>
                        <p style="color:#475569;">Vous avez repéré un protégé qui vous touche sur notre site ? Nous vous invitons à lire attentivement l'ensemble des informations d'adoption, puis à nous contacter par téléphone ou par e-mail.</p>
                        <p style="color:#475569;">Un premier échange nous permettra de vérifier que votre mode de vie, votre environnement et vos attentes correspondent aux besoins spécifiques de l'animal souhaité. Si tout est compatible, nous conviendrons d'un rendez-vous afin de rencontrer l'animal à <strong>Viry-Châtillon (91)</strong>.</p>
                        
                        <div style="background:#eef7fc;border-left:4px solid #1982c4;padding:1rem 1.25rem;border-radius:0 8px 8px 0;margin-top:1rem;">
                            <strong style="color:#0c4a6e;">📍 Conditions géographiques :</strong>
                            <span style="color:#334155;"> Les adoptions sont réservées aux personnes résidant en <strong>Île-de-France</strong>. Cette proximité nous permet de travailler avec notre réseau de vétérinaires partenaires, d'assurer un suivi sérieux et d'accompagner efficacement les adoptants tout au long de l'intégration.</span>
                        </div>
                    </div>

                    <!-- Étape 2 -->
                    <div style="background:#ffffff;border:1px solid #e2e8f0;padding:1.75rem;border-radius:14px;box-shadow:0 4px 12px rgba(0,0,0,0.03);">
                        <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem;">
                            <span style="background:#1982c4;color:#fff;font-weight:800;font-size:1.1rem;width:40px;height:40px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;flex-shrink:0;">2</span>
                            <h3 style="margin:0;color:#0f172a;font-size:1.3rem;">Étape 2 : La pré-adoption (Période d'essai de 3 semaines)</h3>
                        </div>
                        <p style="color:#475569;">Si la rencontre est concluante pour vous comme pour l'animal, vous signez un <strong>contrat de pré-adoption</strong> et remettez un chèque correspondant au montant de l'adoption. L'animal rejoint alors votre foyer pour une <strong>période d'essai de trois semaines</strong> :</p>
                        <ul style="color:#475569;padding-left:1.25rem;">
                            <li>L'animal reste juridiquement sous la responsabilité de l'association ;</li>
                            <li>Vous l'accueillez et prenez soin de lui sous votre responsabilité civile ;</li>
                            <li>Nos bénévoles restent disponibles 7j/7 pour vous conseiller et vous accompagner ;</li>
                            <li>Le règlement des frais d'adoption est alors encaissé ;</li>
                            <li>En cas de réelle difficulté insurmontable, l'association s'engage à reprendre l'animal et vous <strong>rembourse l'intégralité des frais d'adoption</strong> préalablement encaissés.</li>
                        </ul>

                        <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(260px, 1fr));gap:1rem;margin-top:1.25rem;">
                            <div style="background:#f8fafc;padding:1rem;border-radius:8px;border:1px solid #e2e8f0;">
                                <strong style="color:#1e293b;">👨‍👩‍👧‍👦 Rencontre familiale recommandée :</strong>
                                <p style="color:#475569;font-size:0.92rem;margin-bottom:0;margin-top:0.35rem;">Nous vous encourageons à venir accompagnés de tous les membres de votre foyer, ainsi que de votre chien si vous en possédez déjà un.</p>
                            </div>
                            <div style="background:#f8fafc;padding:1rem;border-radius:8px;border:1px solid #e2e8f0;">
                                <strong style="color:#1e293b;">📦 Kit de transition fourni :</strong>
                                <p style="color:#475569;font-size:0.92rem;margin-bottom:0;margin-top:0.35rem;">Pour faciliter son adaptation, nous fournissons une réserve de nourriture et le petit matériel nécessaire à son arrivée (à restituer ensuite à l'association).</p>
                            </div>
                        </div>
                    </div>

                    <!-- Étape 3 -->
                    <div style="background:#ffffff;border:1px solid #e2e8f0;padding:1.75rem;border-radius:14px;box-shadow:0 4px 12px rgba(0,0,0,0.03);">
                        <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem;">
                            <span style="background:#2b9348;color:#fff;font-weight:800;font-size:1.1rem;width:40px;height:40px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;flex-shrink:0;">3</span>
                            <h3 style="margin:0;color:#0f172a;font-size:1.3rem;">Étape 3 : L'adoption définitive</h3>
                        </div>
                        <p style="color:#475569;">À l'issue des trois semaines, si l'intégration s'est déroulée avec succès, nous procédons à l'adoption définitive. Vous signez alors le <strong>contrat d'adoption définitive</strong>, qui formalise vos engagements envers l'animal tout au long de sa vie.</p>
                        <p style="color:#475569;margin-bottom:0;">L'association conserve un droit de suivi et de contrôle du bien-être de l'animal. La carte d'identification ICAD (puce électronique) est transférée à votre nom dans un délai maximal de deux mois.</p>
                    </div>
                </div>

                <!-- Garanties & Documents -->
                <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(300px, 1fr));gap:1.5rem;margin:3rem 0;">
                    <div style="background:#ffffff;border:1px solid #e2e8f0;padding:1.5rem;border-radius:12px;">
                        <h3 style="color:#d90429;margin-top:0;display:flex;align-items:center;gap:8px;">
                            <span>🩺</span> Stérilisation obligatoire
                        </h3>
                        <p style="color:#475569;font-size:0.95rem;">La stérilisation est une <strong>condition indispensable à toute adoption</strong>. Chaque année, des milliers d'animaux sont abandonnés ou naissent sans perspective de foyer. Notre mission prioritaire est de contribuer à enrayer cette surpopulation animale.</p>
                    </div>

                    <div style="background:#ffffff;border:1px solid #e2e8f0;padding:1.5rem;border-radius:12px;">
                        <h3 style="color:#1e293b;margin-top:0;display:flex;align-items:center;gap:8px;">
                            <span>📄</span> Documents à fournir
                        </h3>
                        <ul style="color:#475569;font-size:0.95rem;padding-left:1.25rem;margin-bottom:0;">
                            <li>Une pièce d'identité officielle ou un passeport en cours de validité ;</li>
                            <li>Un justificatif de domicile récent (- de 3 mois) ;</li>
                            <li>Une attestation d'assurance responsabilité civile ;</li>
                            <li>Un chèque correspondant au montant de l'adoption.</li>
                        </ul>
                    </div>

                    <div style="background:#ffffff;border:1px solid #e2e8f0;padding:1.5rem;border-radius:12px;grid-column:1 / -1;">
                        <h3 style="color:#1e293b;margin-top:0;display:flex;align-items:center;gap:8px;">
                            <span>🎒</span> Matériel obligatoire le jour de l'adoption
                        </h3>
                        <p style="color:#475569;margin-bottom:0.75rem;"><strong>Aucun animal ne pourra quitter l'association sans ce matériel de sécurité obligatoire :</strong></p>
                        <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(240px, 1fr));gap:1rem;">
                            <div style="background:#f8fafc;padding:0.9rem;border-radius:8px;">
                                <strong>Pour un chat :</strong> Une caisse de transport solide, rigide et en parfait état de verrouillage.
                            </div>
                            <div style="background:#f8fafc;padding:0.9rem;border-radius:8px;">
                                <strong>Pour un chien :</strong> Une laisse adaptée, ainsi qu'un collier ou un harnais parfaitement ajusté à sa morphologie.
                            </div>
                        </div>
                        <p style="color:#64748b;font-size:0.85rem;margin-top:0.75rem;margin-bottom:0;">* Une caution pourra être demandée pour le matériel mis à disposition par l'association (restituée lors du retour du matériel).</p>
                    </div>
                </div>

                <!-- Section Tarifs 2026 -->
                <div id="tarifs-adoption" style="margin-top:3.5rem;margin-bottom:3rem;">
                    <div style="text-align:center;margin-bottom:2rem;">
                        <span style="background:#e8f4fd;color:#1982c4;font-weight:700;padding:4px 14px;border-radius:20px;font-size:0.85rem;text-transform:uppercase;letter-spacing:0.5px;">Grille Tarifaire Officielle</span>
                        <h2 style="color:#0f172a;font-size:1.8rem;margin-top:0.5rem;margin-bottom:0.5rem;">Tarifs d'adoption 2026</h2>
                        <p style="color:#64748b;max-width:700px;margin:0 auto;">La participation financière demandée contribue à couvrir une partie des frais vétérinaires et d'entretien engagés par l'association pour chaque animal secouru.</p>
                    </div>

                    <!-- Ce que comprennent les frais -->
                    <div style="background:#f8fafc;border:1px solid #e2e8f0;padding:1.5rem;border-radius:12px;margin-bottom:2rem;">
                        <h4 style="color:#0f172a;margin-top:0;margin-bottom:0.75rem;font-size:1.05rem;">✅ Les frais d'adoption comprennent systématiquement :</h4>
                        <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(220px, 1fr));gap:0.75rem;">
                            <div style="display:flex;align-items:center;gap:8px;color:#334155;font-size:0.92rem;">
                                <span style="color:#2b9348;">✓</span> Identification ICAD (puce / tatouage)
                            </div>
                            <div style="display:flex;align-items:center;gap:8px;color:#334155;font-size:0.92rem;">
                                <span style="color:#2b9348;">✓</span> Primo-vaccination & rappel complet
                            </div>
                            <div style="display:flex;align-items:center;gap:8px;color:#334155;font-size:0.92rem;">
                                <span style="color:#2b9348;">✓</span> Test FIV/FeLV (chats de + de 6 mois)
                            </div>
                            <div style="display:flex;align-items:center;gap:8px;color:#334155;font-size:0.92rem;">
                                <span style="color:#2b9348;">✓</span> Antiparasitaires & vermifuges
                            </div>
                            <div style="display:flex;align-items:center;gap:8px;color:#334155;font-size:0.92rem;">
                                <span style="color:#2b9348;">✓</span> Stérilisation / Castration
                            </div>
                            <div style="display:flex;align-items:center;gap:8px;color:#334155;font-size:0.92rem;">
                                <span style="color:#2b9348;">✓</span> Nourriture premium durant l'accueil
                            </div>
                        </div>
                    </div>

                    <!-- Placeholder où le composant Django dynamique injecte les tarifs administrables -->
                    <!-- ADOPTION_TARIFFS_TABLE_DYNAMIC -->
                </div>

                <!-- Association loi 1901 & Paiements -->
                <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:1.5rem;margin:3rem 0;">
                    <div style="background:#ffffff;border:1px solid #e2e8f0;padding:1.5rem;border-radius:12px;">
                        <h3 style="color:#0f172a;margin-top:0;">🤝 Association à but non lucratif</h3>
                        <p style="color:#475569;font-size:0.95rem;margin-bottom:0;"><strong>Rêves de Chiens</strong> est régie par la loi de 1901. L'intégralité des sommes perçues est consacrée au fonctionnement de l'association et aux soins des animaux. Aucun bénévole, famille d'accueil ou membre n'en retire un bénéfice personnel.</p>
                    </div>

                    <div style="background:#fef2f2;border:1px solid #fecaca;padding:1.5rem;border-radius:12px;">
                        <h3 style="color:#991b1b;margin-top:0;">🚫 Modes de paiement non acceptés</h3>
                        <p style="color:#7f1d1d;font-size:0.95rem;margin-bottom:0.5rem;">En raison de trop nombreux impayés passés, nous <strong>n'acceptons plus</strong> :</p>
                        <ul style="color:#7f1d1d;font-size:0.95rem;padding-left:1.25rem;margin-bottom:0;">
                            <li>Les paiements en plusieurs fois ;</li>
                            <li>Les paiements différés ;</li>
                            <li>Les chèques émis depuis l'étranger.</li>
                        </ul>
                    </div>
                </div>

                <!-- Anticiper le coût de la vie avec un animal -->
                <div style="background:#f8fafc;border:1px solid #cbd5e1;padding:1.75rem;border-radius:14px;margin:3rem 0;">
                    <h3 style="color:#0f172a;margin-top:0;font-size:1.25rem;">💶 Anticiper le coût de la vie avec un animal</h3>
                    <p style="color:#475569;">Une alimentation de qualité est essentielle pour préserver la santé et la longévité de votre compagnon :</p>
                    <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(260px, 1fr));gap:1rem;margin:1rem 0;">
                        <div style="background:#ffffff;padding:1rem;border-radius:8px;border:1px solid #e2e8f0;">
                            <strong style="color:#1982c4;">🐕 Pour un chien :</strong>
                            <p style="color:#475569;font-size:0.92rem;margin:0.25rem 0 0 0;">Un sac de 15 kg de croquettes de qualité coûte entre <strong>70 € et 100 €</strong>. Un grand chien (type berger allemand) consomme environ 15 kg par mois.</p>
                        </div>
                        <div style="background:#ffffff;padding:1rem;border-radius:8px;border:1px solid #e2e8f0;">
                            <strong style="color:#8338ec;">🐈 Pour un chat :</strong>
                            <p style="color:#475569;font-size:0.92rem;margin:0.25rem 0 0 0;">Prévoir entre <strong>1,5 et 2 kg</strong> de croquettes par mois, ainsi que l'achat régulier de litière de qualité.</p>
                        </div>
                    </div>
                </div>

                <!-- Rappel de la réglementation -->
                <div style="background:#ffffff;border:1px solid #e2e8f0;padding:1.75rem;border-radius:14px;margin:3rem 0;">
                    <h3 style="color:#0f172a;margin-top:0;font-size:1.25rem;">⚖️ Rappel de la réglementation en vigueur</h3>
                    <ul style="color:#475569;padding-left:1.25rem;line-height:1.7;">
                        <li><strong>Identification obligatoire :</strong> L'identification des chiens et chats est obligatoire avant toute cession, gratuite ou payante (chiens de + de 4 mois nés après le 06/01/1999 ; chats de + de 7 mois nés après le 01/01/2012).</li>
                        <li><strong>Certificat d'engagement et de connaissances :</strong> Doit être obligatoirement signé au moins <strong>7 jours avant l'adoption</strong> (Loi n° 2021-1539 du 30 nov 2021) pour sensibiliser et éviter les achats coup de cœur.</li>
                        <li><strong>Mise à jour ICAD :</strong> Tout changement d'adresse, de propriétaire ou décès doit être immédiatement signalé au fichier national ICAD.</li>
                        <li><strong>Voyager dans l'UE :</strong> L'animal doit être identifié (puce électronique), valablement vacciné contre la rage et disposer d'un passeport européen délivré par un vétérinaire habilité.</li>
                    </ul>
                </div>

                <div style="text-align:center;margin-top:3rem;">
                    <a href="/formulaire-adoption/" class="btn btn-primary btn-lg" style="margin-right:1rem;">Remplir le formulaire d'adoption &rarr;</a>
                    <a href="/articles/" class="btn btn-outline btn-lg">Découvrir nos protégés</a>
                </div>
                """
            },

            # Page 3: Formulaire d'adoption
            {
                "title": "Formulaire d'adoption",
                "slug": "formulaire-adoption",
                "seo_title": "Formulaire d'adoption chien ou chat - Rêves de Chiens",
                "seo_description": "Accédez aux formulaires d'adoption Chien et Chat de l'association Rêves de Chiens.",
                "content": """
                <div class="cms-page-hero" style="background:linear-gradient(135deg, #eef7fc 0%, #ffffff 100%);padding:2.5rem;border-radius:16px;border:1px solid #d0e7f7;text-align:center;margin-bottom:2.5rem;">
                    <h2 style="color:#1982c4;margin-top:0;font-size:1.8rem;">Dossier de candidature à l'adoption</h2>
                    <p class="lead" style="max-width:700px;margin:0 auto;color:#334155;font-size:1.1rem;line-height:1.6;">
                        Vous souhaitez adopter un de nos protégés ? Choisissez le formulaire correspondant à l'espèce pour initier votre démarche auprès de nos bénévoles.
                    </p>
                </div>

                <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(300px, 1fr));gap:2rem;margin:3rem 0;">
                    <!-- Option Chien -->
                    <div style="background:#ffffff;border:2px solid #1982c4;border-radius:16px;padding:2rem;text-align:center;box-shadow:0 6px 18px rgba(25,130,196,0.08);display:flex;flex-direction:column;justify-content:space-between;">
                        <div>
                            <span style="font-size:3.5rem;display:inline-block;margin-bottom:1rem;">🐕</span>
                            <h3 style="color:#1982c4;margin-top:0;font-size:1.4rem;">Formulaire d'adoption Chien</h3>
                            <p style="color:#475569;font-size:0.95rem;line-height:1.6;">
                                Chiots, adultes et seniors. Renseignez votre environnement (maison/appartement, jardin), votre composition familiale et votre rythme de vie.
                            </p>
                        </div>
                        <div style="margin-top:1.5rem;">
                            <a href="/contact/?category=adoption&species=chien" class="btn btn-primary btn-block" style="padding:0.9rem 1.5rem;font-size:1rem;font-weight:700;">
                                Remplir la demande pour un Chien &rarr;
                            </a>
                        </div>
                    </div>

                    <!-- Option Chat -->
                    <div style="background:#ffffff;border:2px solid #8338ec;border-radius:16px;padding:2rem;text-align:center;box-shadow:0 6px 18px rgba(131,56,236,0.08);display:flex;flex-direction:column;justify-content:space-between;">
                        <div>
                            <span style="font-size:3.5rem;display:inline-block;margin-bottom:1rem;">🐈</span>
                            <h3 style="color:#8338ec;margin-top:0;font-size:1.4rem;">Formulaire d'adoption Chat</h3>
                            <p style="color:#475569;font-size:0.95rem;line-height:1.6;">
                                Chatons et chats adultes. Précisez la sécurisation de vos ouvertures/balcons et la présence éventuelle d'autres compagnons.
                            </p>
                        </div>
                        <div style="margin-top:1.5rem;">
                            <a href="/contact/?category=adoption&species=chat" class="btn btn-primary btn-block" style="background:#8338ec;border-color:#8338ec;padding:0.9rem 1.5rem;font-size:1rem;font-weight:700;">
                                Remplir la demande pour un Chat &rarr;
                            </a>
                        </div>
                    </div>
                </div>

                <div style="background:#f8fafc;border:1px solid #e2e8f0;padding:1.5rem;border-radius:12px;margin:2rem 0;">
                    <h4 style="margin-top:0;color:#0f172a;">📌 Rappels importants avant de postuler :</h4>
                    <ul style="color:#475569;margin-bottom:0;padding-left:1.25rem;">
                        <li>Les adoptions sont réservées aux résidents d'<strong>Île-de-France</strong>.</li>
                        <li>Conformément à la loi, un <strong>certificat d'engagement et de connaissances</strong> doit être signé au minimum 7 jours avant l'adoption.</li>
                        <li>Pour toute question préalable, notre équipe de bénévoles reste à votre écoute via notre <a href="/contact/" style="color:#1982c4;text-decoration:underline;">formulaire de contact</a>.</li>
                    </ul>
                </div>
                """
            },

            # Page 4: A Propos
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

            # Page 5: Familles d'accueil
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

            # Page 6: Conditions d'abandon
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

            # Page 7: Dons & Parrainages
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

            # Page 8: Mentions légales
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

        # 4. Setup Navigation Menus
        self.stdout.write("Setting up Navigation Menus...")

        # Ensure Categories exist for dynamic menu links
        les_adoptes_cat, _ = Category.objects.get_or_create(slug="les-adoptes", defaults={"name": "Les Adoptés"})

        # 1. Main Header Menu
        main_menu, _ = Menu.objects.get_or_create(slug="main", defaults={"name": "Menu Principal"})
        main_menu.items.all().delete()
        MenuItem.objects.create(menu=main_menu, title="Accueil", url="/", position=1)
        MenuItem.objects.create(menu=main_menu, title="Adoption", url="/articles/", position=2)
        MenuItem.objects.create(menu=main_menu, title="Puis-je adopter ?", linked_page=created_pages.get("puis-je-adopter"), position=3)
        MenuItem.objects.create(menu=main_menu, title="Conditions & Tarifs", linked_page=created_pages.get("conditions-adoption"), position=4)
        MenuItem.objects.create(menu=main_menu, title="Formulaire d'adoption", linked_page=created_pages.get("formulaire-adoption"), position=5)
        MenuItem.objects.create(menu=main_menu, title="Agir & Soutenir", linked_page=created_pages.get("dons-parrainages"), position=6)
        MenuItem.objects.create(menu=main_menu, title="L'Association", linked_page=created_pages.get("a-propos"), position=7)
        MenuItem.objects.create(menu=main_menu, title="Contact", url="/contact/", position=8)

        # 2. Adoptions Sidebar Menu
        adoptions_menu, _ = Menu.objects.get_or_create(slug="adoptions", defaults={"name": "Adopter un animal"})
        adoptions_menu.items.all().delete()
        MenuItem.objects.create(menu=adoptions_menu, title="Tous nos protégés", url="/articles/", position=1)
        MenuItem.objects.create(menu=adoptions_menu, title="Puis-je adopter ?", linked_page=created_pages.get("puis-je-adopter"), position=2)
        MenuItem.objects.create(menu=adoptions_menu, title="Conditions d'adoption & Tarifs", linked_page=created_pages.get("conditions-adoption"), position=3)
        MenuItem.objects.create(menu=adoptions_menu, title="Formulaire d'adoption", linked_page=created_pages.get("formulaire-adoption"), position=4)
        MenuItem.objects.create(menu=adoptions_menu, title="Nos chiens", url="/categories/chiens/", position=5)
        MenuItem.objects.create(menu=adoptions_menu, title="Nos chats", url="/categories/chats/", position=6)
        MenuItem.objects.create(menu=adoptions_menu, title="🚨 Recherche FA urgente", url="/categories/urgences/", position=7)
        MenuItem.objects.create(menu=adoptions_menu, title="Les Heureux Adoptés", linked_category=les_adoptes_cat, position=8)

        # 3. Plus d'infos Sidebar Menu
        plus_infos_menu, _ = Menu.objects.get_or_create(slug="plus_infos", defaults={"name": "En savoir plus"})
        plus_infos_menu.items.all().delete()
        MenuItem.objects.create(menu=plus_infos_menu, title="Qui sommes-nous ?", linked_page=created_pages.get("a-propos"), position=1)
        MenuItem.objects.create(menu=plus_infos_menu, title="Devenir Famille d'Accueil", linked_page=created_pages.get("familles-accueil"), position=2)
        MenuItem.objects.create(menu=plus_infos_menu, title="Conditions d'abandon & prise en charge", linked_page=created_pages.get("conditions-abandon"), position=3)
        MenuItem.objects.create(menu=plus_infos_menu, title="Faire un don / Parrainer", linked_page=created_pages.get("dons-parrainages"), position=4)
        MenuItem.objects.create(menu=plus_infos_menu, title="Que sont-ils devenus ?", linked_category=les_adoptes_cat, position=5)
        MenuItem.objects.create(menu=plus_infos_menu, title="Mentions légales & Transparence", linked_page=created_pages.get("mentions-legales"), position=6)

        # 4. Footer Menu
        footer_menu, _ = Menu.objects.get_or_create(slug="footer", defaults={"name": "Menu Pied de Page"})
        footer_menu.items.all().delete()
        MenuItem.objects.create(menu=footer_menu, title="Accueil", url="/", position=1)
        MenuItem.objects.create(menu=footer_menu, title="À l'adoption", url="/articles/", position=2)
        MenuItem.objects.create(menu=footer_menu, title="Puis-je adopter ?", linked_page=created_pages.get("puis-je-adopter"), position=3)
        MenuItem.objects.create(menu=footer_menu, title="Conditions & Tarifs", linked_page=created_pages.get("conditions-adoption"), position=4)
        MenuItem.objects.create(menu=footer_menu, title="Formulaire d'adoption", linked_page=created_pages.get("formulaire-adoption"), position=5)
        MenuItem.objects.create(menu=footer_menu, title="Devenir FA", linked_page=created_pages.get("familles-accueil"), position=6)
        MenuItem.objects.create(menu=footer_menu, title="Dons & Soutiens", linked_page=created_pages.get("dons-parrainages"), position=7)
        MenuItem.objects.create(menu=footer_menu, title="Mentions légales", linked_page=created_pages.get("mentions-legales"), position=8)
        MenuItem.objects.create(menu=footer_menu, title="Contact", url="/contact/", position=9)

        self.stdout.write(self.style.SUCCESS("Successfully seeded all Rêves de Chiens CMS pages, tariffs, and dynamic menus!"))
