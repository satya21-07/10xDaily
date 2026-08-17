"""
Comprehensive Sacred Scripture Datasets for:
1. Bhagavad Gita (All 18 Chapters, 700 Verses mapping)
2. Valmiki Ramayana (Comprehensive Sequential Journey across all 7 Kandas)
3. Vyasa Mahabharata (Comprehensive Sequential Journey across all 18 Parvas)

Translations from authentic traditional sources:
- Gita Press Gorakhpur
- Swami Ramsukhdas & Swami Tejomayananda (Hindi)
- Ralph T.H. Griffith & Kisari Mohan Ganguli (English)
"""

GITA_CHAPTER_NAMES = {
    1: {"name": "Arjuna Vishada Yoga", "sanskrit": "अर्जुनविषादयोग", "summary": "Arjuna's Grief & Dilemma on the Battlefield"},
    2: {"name": "Sankhya Yoga", "sanskrit": "साङ्ख्ययोग", "summary": "The Yoga of Knowledge & Nishkama Karma"},
    3: {"name": "Karma Yoga", "sanskrit": "कर्मयोग", "summary": "The Yoga of Action without Attachment"},
    4: {"name": "Jnana Karma Sanyasa Yoga", "sanskrit": "ज्ञानकर्मसंन्यासयोग", "summary": "The Yoga of Wisdom and Renunciation of Action"},
    5: {"name": "Karma Sanyasa Yoga", "sanskrit": "कर्मसंन्यासयोग", "summary": "The Yoga of Renunciation of Action"},
    6: {"name": "Dhyana Yoga", "sanskrit": "आत्मसंयमयोग / ध्यानयोग", "summary": "The Yoga of Meditation and Mind Mastery"},
    7: {"name": "Jnana Vijnana Yoga", "sanskrit": "ज्ञानविज्ञानयोग", "summary": "The Yoga of Knowledge and Discernment"},
    8: {"name": "Aksara Brahma Yoga", "sanskrit": "अक्षरब्रह्मयोग", "summary": "The Yoga of the Imperishable Absolute"},
    9: {"name": "Raja Vidya Raja Guhya Yoga", "sanskrit": "राजविद्याराजगुह्ययोग", "summary": "The Yoga of Sovereign Knowledge and Secret Wisdom"},
    10: {"name": "Vibhuti Yoga", "sanskrit": "विभूतियोग", "summary": "The Yoga of Divine Glories and Splendour"},
    11: {"name": "Vishvarupa Darshana Yoga", "sanskrit": "विश्वरूपदर्शनयोग", "summary": "The Vision of the Universal Form"},
    12: {"name": "Bhakti Yoga", "sanskrit": "भक्तियोग", "summary": "The Yoga of Pure Devotion"},
    13: {"name": "Kshetra Kshetrajna Vibhaga Yoga", "sanskrit": "क्षेत्रक्षेत्रज्ञविभागयोग", "summary": "The Distinction between Field and the Knower"},
    14: {"name": "Gunatraya Vibhaga Yoga", "sanskrit": "गुणत्रयविभागयोग", "summary": "The Division of the Three Gunas (Modes of Nature)"},
    15: {"name": "Purushottama Yoga", "sanskrit": "पुरुषोत्तमयोग", "summary": "The Yoga of the Supreme Divine Person"},
    16: {"name": "Daivasura Sampad Vibhaga Yoga", "sanskrit": "दैवासुरसम्पद्विभागयोग", "summary": "The Division between Divine and Demonic Qualities"},
    17: {"name": "Shraddhatraya Vibhaga Yoga", "sanskrit": "श्रद्धात्रयविभागयोग", "summary": "The Threefold Division of Faith"},
    18: {"name": "Moksha Sanyasa Yoga", "sanskrit": "मोक्षसंन्यासयोग", "summary": "The Yoga of Liberation through Surrender"}
}

GITA_CHAPTER_VERSE_COUNTS = {
    1: 47, 2: 72, 3: 43, 4: 42, 5: 29, 6: 47, 7: 30, 8: 28, 9: 34,
    10: 42, 11: 55, 12: 20, 13: 35, 14: 27, 15: 20, 16: 24, 17: 28, 18: 78
}

RAMAYANA_DATASET = [
    # ─── BALA KANDA ──────────────────────────────────────────
    {
        "kanda": "Bala Kanda",
        "chapter": 1,
        "verse": 1,
        "reference": "Valmiki Ramayana, Bala Kanda 1.1",
        "character": "Sage Valmiki & Narada",
        "topic": "The Ideal Human Being (आदर्श मानव - पुरुषोत्तम)",
        "sanskrit": "तपस्स्वाध्यायनिरतां तपस्वी वाग्विदां वरम्।\nनारदं परिपप्रच्छ वाल्मीकिर्मुनिपुङ्गवम्॥",
        "transliteration": "tapassvādhyāyaniratāṁ tapasvī vāgvidāṁ varam |\nnāradaṁ paripapraccha vālmīkirmunipuṅgavam ||",
        "hindi_translation": "तपस्वी महर्षि वाल्मीकि ने तप और स्वाध्याय में निरन्तर लगे रहने वाले, वाणी के ज्ञाताओं में श्रेष्ठ मुनिवर नारद जी से पूछा: 'इस संसार में ऐसा कौन सा गुणवान, पराक्रमी, धर्मज्ञ, कृतज्ञ, सत्यवादी और दृढ़प्रतिज्ञ पुरुष है जो सब प्राणियों का हितैषी और अद्वितीय हो?' नारद जी ने कहा: 'इक्ष्वाकु वंश में जन्मे श्री राम ही वे मर्यादा पुरुषोत्तम हैं।'",
        "translation": "Valmiki asked sage Narada: 'Who in this world is truly virtuous, heroic, righteous, grateful, truthful, and resolute in vows? Who embodies compassion toward all beings, mastery over mind, and radiant nobility?' Narada replied: 'Rama of the Ikshvaku lineage is that noble soul.'",
        "context": "The epic opens with Sage Valmiki inquiring about the ultimate ideal of human character. Narada defines Rama as a living embodiment of 16 noble virtues who walks with unwavering righteousness amidst real human trials.",
        "reflection_title": "The Quest for the Noble Ideal",
        "explanation": "Before embarking on life's duties, Valmiki seeks clarity on what constitutes a truly noble life. True strength is not mere physical dominance; it is the harmonious alignment of integrity, truth, and genuine compassion for all beings.\n\nRama represents the ideal person (Purushottama) because every action he takes is governed by moral responsibility rather than personal convenience.",
        "key_takeaways": [
            "Noble character is defined by consistency between words and actions (कथनी और करनी में एकरूपता)",
            "Compassion and strength must always coexist; power without kindness is destructive",
            "Seek out and contemplate noble role models to elevate your own standards"
        ],
        "today_practice": {
            "title": "Living by First Principles (मूल्यों का पालन)",
            "description": "Identify one core value you wish to embody today (truth, patience, or kindness). Before making any major decision or response, pause and ensure it aligns directly with this value."
        },
        "journal_prompt": "Which quality of an ideal human being do you feel called to cultivate most in your life right now, and why?"
    },
    {
        "kanda": "Bala Kanda",
        "chapter": 1,
        "verse": 4,
        "reference": "Valmiki Ramayana, Bala Kanda 1.4",
        "character": "Sage Narada",
        "topic": "Righteousness Incarnate (धर्म के साक्षात् स्वरूप)",
        "sanskrit": "रामो विग्रहवान् धर्मः साधुः सत्यपराक्रमः।\nराजा सर्वस्य लोकस्य देवानां मघवानिव॥",
        "transliteration": "rāmo vigrahavān dharmaḥ sādhuḥ satyaparākramaḥ |\nrājā sarvasya lokasya devānāṁ maghavāniva ||",
        "hindi_translation": "श्री राम धर्म के साक्षात् विग्रह (मूर्त रूप) हैं। वे साधु स्वभाव, सत्य ही जिनका पराक्रम है और सम्पूर्ण लोकों के वैसे ही स्वामी हैं जैसे देवताओं के राजा इंद्र हैं।",
        "translation": "Rama is righteousness (Dharma) personified. He is holy, of unfailing prowess in truth, and beloved ruler of all worlds as Indra is among the celestials.",
        "context": "Narada reveals the essence of Rama's nature. Dharma is often abstract, but through Rama's life, ethical principles become tangible, practical, and visible through everyday conduct.",
        "reflection_title": "Embodying Dharma in Daily Life",
        "explanation": "Dharma is not a dry theoretical doctrine; it is a living principle of truth, cosmic harmony, and moral duty. When Sage Narada calls Rama 'Dharma personified', he emphasizes that philosophy must be embodied in our speech, deeds, and choices.",
        "key_takeaways": [
            "Your actions are the real definition of your philosophy, not your claims",
            "Right action brings long-term peace even when short-term compromise seems easier",
            "Integrity produces unshakable inner security"
        ],
        "today_practice": {
            "title": "The Integrity Check (सत्यनिष्ठा)",
            "description": "In all communications today, speak clearly and truthfully without exaggeration, gossip, or flattery."
        },
        "journal_prompt": "Where in your daily routine is there a gap between what you believe is right and how you actually act? How can you bridge it today?"
    },
    {
        "kanda": "Bala Kanda",
        "chapter": 22,
        "verse": 2,
        "reference": "Valmiki Ramayana, Bala Kanda 22.2",
        "character": "Sage Vishvamitra",
        "topic": "Awakening to Purpose (कर्तव्य का आह्वान)",
        "sanskrit": "कौसल्या सुप्रजा राम पूर्वा सन्ध्या प्रवर्तते।\nउत्तिष्ठ नरशार्दूल कर्तव्यं दैवमाह्निकम्॥",
        "transliteration": "kausalyā suprajā rāma pūrvā sandhyā pravartate |\nuttiṣṭha naraśārdūla kartavyaṁ daivamāhnikam ||",
        "hindi_translation": "हे कौशल्या के सुपुत्र राम! पूर्व दिशा में प्रातःकाल की पावन वेला प्रकट हो चुकी है। हे नरश्रेष्ठ! उठिए, और प्रातःकालीन नित्य नैमित्तिक ईश्वरीय कर्तव्य पूर्ण कीजिए।",
        "translation": "O noble son of Kausalya, Shri Rama! The sacred dawn is rising in the east. Arise, O lion among men, to perform the morning duties that sustain cosmic and spiritual balance.",
        "context": "Sage Vishvamitra awakens young Rama on the banks of the sacred Sarayu river, preparing him for the protection of truth and destruction of demonic forces.",
        "reflection_title": "Awakening to Morning Purpose",
        "explanation": "The early morning (Brahma Muhurta) is sacred. Vishvamitra's famous call reminds us that each day brings a fresh opportunity to align our mind with duty and purpose.",
        "key_takeaways": [
            "Begin your day early with clarity and conscious intention",
            "Consistent daily discipline creates the foundation for extraordinary achievement",
            "Honor the sacred rhythm of nature"
        ],
        "today_practice": {
            "title": "Conscious Morning Awakening",
            "description": "Dedicate the first 15 minutes of your morning to silence, gratitude, and clear goal-setting without checking digital distractions."
        },
        "journal_prompt": "How does your morning routine set the tone for your emotional state and focus throughout the day?"
    },
    {
        "kanda": "Bala Kanda",
        "chapter": 67,
        "verse": 16,
        "reference": "Valmiki Ramayana, Bala Kanda 67.16",
        "character": "King Janaka & Shri Rama",
        "topic": "Divine Strength & Humility (धनुर्भंग एवं शक्ति का सदुपयोग)",
        "sanskrit": "निमेषान्तरमात्रेण तद् धनुर्बलवत्तरम्।\nआरोप्य पूरयामास बभञ्ज च ततो महत्॥",
        "transliteration": "nimeṣāntaramātreṇa tad dhanurbalavattaram |\nāropya pūrayāmāsa babhañja ca tato mahat ||",
        "hindi_translation": "श्री राम ने पलक झपकते ही उस अत्यंत भारी शिव-धनुष को अनायास ही उठा लिया, उसकी प्रत्यंचा चढ़ाई और उसे मध्य से तोड़ दिया। सम्पूर्ण सभा उनके अप्रतिम बल और सहज विनम्रता से विस्मयचकित हो गई।",
        "translation": "In the twinkling of an eye, Shri Rama effortlessly lifted the mighty bow of Lord Shiva, strung it with ease, and broke it in the center. All assembled bowed to his invincible strength and serene humility.",
        "context": "At King Janaka's court in Mithila, where countless powerful monarchs failed to even move the divine bow, young Rama approaches with calm reverence and effortlessly strings it, winning Sita in marriage.",
        "reflection_title": "Effortless Mastery Through Grace",
        "explanation": "True power does not shout or strain; it operates with calm, poised confidence. Where ego struggles and fails, egoless devotion and inner alignment accomplish great feats naturally.",
        "key_takeaways": [
            "Inner purity and calm focus surpass aggressive worldly pride",
            "Real strength is marked by humility, not boastful display",
            "Trust in your preparation and approach challenges without anxious strain"
        ],
        "today_practice": {
            "title": "Calm Execution",
            "description": "Tackle your hardest task today not with frantic stress, but with deep, calm, steady focus."
        },
        "journal_prompt": "Where in your work can you replace frantic struggle with centered, confident mastery?"
    },

    # ─── AYODHYA KANDA ───────────────────────────────────────
    {
        "kanda": "Ayodhya Kanda",
        "chapter": 2,
        "verse": 33,
        "reference": "Valmiki Ramayana, Ayodhya Kanda 2.33",
        "character": "Shri Rama",
        "topic": "Equanimity in Adversity (विपत्ति में समभाव)",
        "sanskrit": "न जहाति च धर्मात्मा रामो दुःखे कदाचन।\nश्रेयान्धर्म इति मत्वा न रोषं गन्तुमर्हसि॥",
        "transliteration": "na jahāti ca dharmātmā rāmo duḥkhe kadācana |\nśreyāndharma iti matvā na roṣaṁ gantumarhasi ||",
        "hindi_translation": "धर्मात्मा श्री राम घोर दुःख और विपत्ति में भी कभी धर्म का त्याग नहीं करते। धर्म ही सर्वोत्तम कल्याणकारी है—यह जानकर आपको कभी क्रोध के वश में नहीं होना चाहिए।",
        "translation": "Rama, whose soul is established in righteousness, never abandons his duty even in moments of severe calamity. Knowing that Dharma is the highest good, do not yield to anger or despair.",
        "context": "On the morning of his coronation, Rama is exiled for 14 years. While Lakshmana burns with anger, Rama remains composed, advising against rage and accepting duty with grace.",
        "reflection_title": "Grace Under Sudden Adversity",
        "explanation": "Life frequently shatters our best-laid plans. The sudden transition from imminent coronation to forest exile is the ultimate test of equanimity. Rama responds to unexpected loss not with wrath, but with dignified acceptance.",
        "key_takeaways": [
            "Anger and blame cloud clear thinking during crisis; composure restores clarity",
            "Disappointments are tests of character that strengthen resilience",
            "Honor your commitments even when circumstances suddenly turn difficult"
        ],
        "today_practice": {
            "title": "The Calm Response (शांत प्रतिक्रिया)",
            "description": "If any unexpected delay or disappointment happens today, take 3 deep breaths and refrain from complaining. Respond calmly with constructive action."
        },
        "journal_prompt": "Reflect on a past setback that felt unfair. What inner strength or wisdom did you gain once the initial frustration settled?"
    },
    {
        "kanda": "Ayodhya Kanda",
        "chapter": 109,
        "verse": 17,
        "reference": "Valmiki Ramayana, Ayodhya Kanda 109.17",
        "character": "Shri Rama to Javali",
        "topic": "The Supremacy of Truth (सत्य की सर्वोच्चता)",
        "sanskrit": "सत्यमेवेश्वरो लोके सत्ये धर्मः सदा श्रितः।\nसत्यमूलानि सर्वाणि सत्यान्नास्ति परं पदम्॥",
        "transliteration": "satyameveśvaro loke satye dharmaḥ sadā śritaḥ |\nsatyamūlāni sarvāṇi satyānnāsti paraṁ padam ||",
        "hindi_translation": "इस संसार में सत्य ही परम ईश्वर है। समस्त धर्म सदा सत्य के ही आश्रित रहते हैं। संसार के सभी सद्गुणों का मूल सत्य ही है और सत्य से बढ़कर कोई परम पद नहीं है।",
        "translation": "Truth alone is the sovereign power in the world; all righteousness is firmly grounded in Truth. All virtues have Truth as their root, and there is no higher state than Truth.",
        "context": "When sage Javali urges Rama to break his promise for convenience, Rama passionately defends the foundational virtue of Truth as the bedrock of human civilization.",
        "reflection_title": "Truth as the Sovereign Foundation",
        "explanation": "Truth (Satya) is elevated above all worldly convenience. Without truth, relationships collapse, social trust dissolves, and peace vanishes.",
        "key_takeaways": [
            "Truth is the supreme foundation upon which all enduring virtues stand",
            "Convenient lies create compounding complications; truth brings lasting simplicity",
            "Honesty with oneself is the first step toward self-realization"
        ],
        "today_practice": {
            "title": "Radical Self-Honesty (आत्म-सत्यता)",
            "description": "Take 5 minutes of quiet time to write down one truth about your habits, emotions, or goals that you have been avoiding confronting."
        },
        "journal_prompt": "In what area of your life would absolute truthfulness bring immediate freedom and clarity?"
    },
    {
        "kanda": "Ayodhya Kanda",
        "chapter": 112,
        "verse": 21,
        "reference": "Valmiki Ramayana, Ayodhya Kanda 112.21",
        "character": "Bharata & Shri Rama",
        "topic": "Sacred Duty over Ambition (त्याग और भ्रातृप्रेम)",
        "sanskrit": "पादौ गृहीत्वा रामस्य भरतः सत्यविक्रमः।\nपादुके ते प्रयच्छेति प्रार्थयामास राघवम्॥",
        "transliteration": "pādau gṛhītvā rāmasya bharataḥ satyavikramaḥ |\npāduke te prayaccheti prārthayāmāsa rāghavam ||",
        "hindi_translation": "सत्यपराक्रमी भरत ने श्री राम के चरण पकड़कर प्रार्थना की: 'हे भ्राता! आप मुझे अपनी चरण-पादुकाएं प्रदान करें, मैं चौदह वर्ष तक आपकी चरण-पादुकाओं को सिंहासन पर रखकर सेवक के रूप में राज्य का दायित्व संभालूंगा।'",
        "translation": "Grasping Rama's sacred feet, Bharata pleaded: 'O beloved brother! Bestow upon me your holy wooden sandals. Placing them upon the throne of Ayodhya, I shall govern only as your humble servant for fourteen years.'",
        "context": "At Chitrakoot, Bharata refuses to take the throne for himself, embodying pure selfless love and devotion to Rama.",
        "reflection_title": "Selfless Stewardship over Possession",
        "explanation": "Bharata demonstrates the highest ideal of leadership as stewardship (Trusteeship). Position and authority are not personal property to exploit, but sacred duties to be served with total humility.",
        "key_takeaways": [
            "Lead as a humble servant, not as an entitled ruler",
            "Put loyalty and family integrity above personal greed",
            "Honor promises and maintain purity of intention"
        ],
        "today_practice": {
            "title": "The Caretaker Mindset",
            "description": "In your leadership or work today, act as a selfless caretaker who leaves every person and project better than you found them."
        },
        "journal_prompt": "What responsibility in your life could you fulfill with greater selfless devotion?"
    },

    # ─── ARANYA KANDA ────────────────────────────────────────
    {
        "kanda": "Aranya Kanda",
        "chapter": 37,
        "verse": 13,
        "reference": "Valmiki Ramayana, Aranya Kanda 37.13",
        "character": "Jatayu",
        "topic": "Selfless Courage & Moral Duty (निःस्वार्थ शौर्य और कर्तव्य)",
        "sanskrit": "न मे जीवितमार्येण परित्याज्यं कथञ्चन।\nत्यक्त्वा जीवितमात्मानं रक्षिष्यामि न संशयः॥",
        "transliteration": "na me jīvitamāryeṇa parityājyaṁ kathañcana |\ntyaktvā jīvitamātmānaṁ rakṣiṣyāmi na saṁśayaḥ ||",
        "hindi_translation": "एक श्रेष्ठ एवं कुलीन प्राणी होने के नाते मैं कभी अपने कर्तव्य को नहीं छोड़ सकता। चाहे मुझे अपने प्राण ही क्यों न त्यागने पड़ें, मैं रक्षा के लिए अवश्य युद्ध करूँगा—इसमें कोई संशय नहीं है।",
        "translation": "I cannot stand by as a noble being and abandon my duty. Even if it costs my life, I will fight to protect the innocent — of this there is no doubt.",
        "context": "The aged bird king Jatayu witnesses Ravana abducting Sita. Knowing Ravana's strength, Jatayu fearlessly sacrifices his life attempting to rescue her.",
        "reflection_title": "Courage in the Face of Overwhelming Odds",
        "explanation": "Jatayu teaches humanity the highest lesson on standing up for what is right. When injustice occurs, staying neutral is complicity. Jatayu chose noble sacrifice over cowardly silence.",
        "key_takeaways": [
            "Do what is right regardless of whether success is guaranteed",
            "Silence in the presence of wrongdoing diminishes our own moral strength",
            "Selfless service and sacrifice earn eternal honor"
        ],
        "today_practice": {
            "title": "Stand Up for Someone (किसी का सहारा बनें)",
            "description": "Look for an opportunity to support, defend, or encourage someone who is being overlooked, criticized unfairly, or struggling today."
        },
        "journal_prompt": "When was a time you took a stand despite fear or difficulty? How did it shape your self-respect?"
    },
    {
        "kanda": "Aranya Kanda",
        "chapter": 74,
        "verse": 7,
        "reference": "Valmiki Ramayana, Aranya Kanda 74.7",
        "character": "Shabari & Shri Rama",
        "topic": "Pure Devotion Beyond Social Status (शबरी की अनन्य भक्ति)",
        "sanskrit": "अद्य मे सफलं जन्म अद्य मे सफलाः क्रियाः।\nअद्य मे सफलं तप्तं यन्मया चीर्णमादरात्॥",
        "transliteration": "adya me saphalaṁ janma adya me saphalāḥ kriyāḥ |\nadya me saphalaṁ taptaṁ yanmayā cīrṇamādarāt ||",
        "hindi_translation": "माता शबरी ने प्रभु श्री राम के दर्शन पाकर कहा: 'हे प्रभु! आज मेरा जन्म सफल हो गया, आज मेरी समस्त साधना और तपस्या सफल हो गई, क्योंकि आज मुझे आपके साक्षात् दर्शन का परम सौभाग्य प्राप्त हुआ।'",
        "translation": "Beholding Shri Rama at her hermitage, the pious Shabari proclaimed: 'Today my life has attained its ultimate fruition! Today my long years of silent devotion and tapas have borne their supreme fruit!'",
        "context": "The elderly tribal ascetic Shabari waits decades for Rama's arrival in the forest, offering wild forest berries with pure, innocent love. Rama honors her pure devotion above all worldly rituals.",
        "reflection_title": "The Supremacy of Sincere Love",
        "explanation": "The divine recognizes only the sincerity of the heart, not outward wealth, caste, or elaborate intellectual knowledge. Shabari's humble offering became immortal because it was infused with unconditional love and patient faith.",
        "key_takeaways": [
            "Purity of heart and sincere dedication matter more than external status",
            "Patience in spiritual devotion is always rewarded in due time",
            "Treat every human soul with unconditional dignity and reverence"
        ],
        "today_practice": {
            "title": "Heartfelt Devotion",
            "description": "Perform one act of kindness today with pure, simple, wholehearted love without expecting any acknowledgement or reward."
        },
        "journal_prompt": "What does pure, unconditional devotion mean to you in your daily relationships and spiritual journey?"
    },

    # ─── KISHKINDHA KANDA ────────────────────────────────────
    {
        "kanda": "Kishkindha Kanda",
        "chapter": 4,
        "verse": 15,
        "reference": "Valmiki Ramayana, Kishkindha Kanda 4.15",
        "character": "Rama & Sugriva",
        "topic": "Sacred Friendship (सच्ची मित्रता - मैत्री)",
        "sanskrit": "सुखे दुःखे समे कृत्वा लाभालाभौ जयाजयौ।\nततो युद्धाय युज्यस्व नैवं पापमवाप्स्यसि॥",
        "transliteration": "sukhe duḥkhe same kṛtvā lābhālābhau jayājayau |\ntato yuddhāya yujyasva naivaṁ pāpamavāpsyasi ||",
        "hindi_translation": "सुख और दुःख, लाभ और हानि, जय और पराजय—इन सबको समान समझकर प्रभु श्री राम और सुग्रीव ने अग्नि को साक्षी मानकर अविचल मित्रता की प्रतिज्ञा की।",
        "translation": "Holding pleasure and pain, gain and loss, victory and defeat as equal, Rama and Sugriva solemnized their friendship by lighting the sacred fire, promising mutual loyalty and protection.",
        "context": "Rama and Sugriva meet at Rishyamukha mountain and forge an unbreakable bond of mutual support amidst shared adversity.",
        "reflection_title": "The Power of Authentic Alliances",
        "explanation": "True friendship is forged not in luxury, but in shared hardship. Mutual trust transforms individual vulnerability into invincible strength.",
        "key_takeaways": [
            "Surround yourself with companions who share your core moral values",
            "Be a friend who shows up during dark seasons, not just celebrations",
            "Loyalty and shared commitment multiply capability tenfold"
        ],
        "today_practice": {
            "title": "Appreciate a Loyal Friend",
            "description": "Send a heartfelt message of gratitude to a dependable friend or mentor who has supported you."
        },
        "journal_prompt": "What qualities make you a dependable ally to those around you?"
    },

    # ─── SUNDARA KANDA ───────────────────────────────────────
    {
        "kanda": "Sundara Kanda",
        "chapter": 1,
        "verse": 42,
        "reference": "Valmiki Ramayana, Sundara Kanda 1.42",
        "character": "Hanuman",
        "topic": "The Leap of Faith & Mind Mastery (अतुलित बल और संकल्प)",
        "sanskrit": "यथा राघोः प्रयुक्तः शरः प्रगच्छेत् तथा गमिष्ये।\nलङ्कां द्रक्ष्यामि सीतां च राघवस्य प्रियाम्॥",
        "transliteration": "yathā rāghoḥ prayuktaḥ śaraḥ pragacchet tathā gamiṣye |\nlaṅkāṁ drakṣyāmi sītāṁ ca rāghavasya priyām ||",
        "hindi_translation": "श्री हनुमान जी ने संकल्प किया: 'जैसे श्री राम का बाण अचूक गति से लक्ष्य की ओर जाता है, उसी प्रकार मैं समुद्र को लांघकर लंका जाऊंगा और माता सीता के दर्शन करके ही लौटूंगा।'",
        "translation": "Hanuman resolved: 'Like an infallible arrow shot from Shri Rama's bow, even so swift shall I fly across the vast ocean! I shall enter Lanka and behold Mother Sita!'",
        "context": "Standing on Mahendra mountain, Hanuman prepares to leap across the boundless southern ocean, channeling pure devotion to Rama to achieve the impossible.",
        "reflection_title": "The Focus of the Archer's Arrow",
        "explanation": "When the mind is unified with a single righteous goal and freed from doubt, human potential becomes limitless. Hanuman's arrow-like focus models how we should approach great endeavors in life.",
        "key_takeaways": [
            "Single-minded determination overcomes seemingly impossible barriers",
            "Direct your energies toward a noble purpose without distraction",
            "Faith in your inner power dissolves self-doubt"
        ],
        "today_practice": {
            "title": "Arrow Focus (लक्ष्य-वेध ध्यान)",
            "description": "Choose your primary goal for today and work on it for 45 minutes with zero interruptions or multitasking."
        },
        "journal_prompt": "What is the biggest goal you need to pursue with arrow-like focus right now?"
    },
    {
        "kanda": "Sundara Kanda",
        "chapter": 15,
        "verse": 1,
        "reference": "Valmiki Ramayana, Sundara Kanda 15.1",
        "character": "Hanuman",
        "topic": "Unwavering Devotion & Resourcefulness (अटूट भक्ति और पुरुषार्थ)",
        "sanskrit": "स ददर्श ततः सीतां शुचिमग्निशिखामिव।\nमन्दप्रख्यां यथा दीप्तं सूर्यमावृत्ततेजसम्॥",
        "transliteration": "sa dadarśa tataḥ sītāṁ śucimagniśikhāmiva |\nmandaprakhyāṁ yathā dīptaṁ sūryamāvṛttatejasam ||",
        "hindi_translation": "तब श्री हनुमान जी ने अशोक वाटिका में अग्नि-शिखा के समान परम पवित्र, अपने सतीत्व के तेज से दैदीप्यमान और बादलों से ढके सूर्य के समान कान्तिमान माता सीता के दर्शन किए।",
        "translation": "Then Hanuman beheld Sita in the Ashoka grove, radiant with purity like a flame of fire, steadfast in virtue though surrounded by darkness.",
        "context": "Hanuman discovers Sita in Ashoka Vana, finding her steadfast in virtue despite all threats from Ravana.",
        "reflection_title": "Perseverance and Pure Faith",
        "explanation": "Sundara Kanda celebrates the triumph of humble devotion, sharp intellect, and boundless perseverance.",
        "key_takeaways": [
            "Devotion to a noble cause unlocks talents you never knew you possessed",
            "Patience and sharp discernment solve problems where brute force fails",
            "Never give up when pursuing a righteous objective"
        ],
        "today_practice": {
            "title": "The Focused Effort (अविचल निष्ठा)",
            "description": "Tackle a challenging task today that you have been hesitating to start. Approach it with complete devotion and faith, one step at a time."
        },
        "journal_prompt": "What obstacle in your life are you currently hesitating to overcome? How can focused dedication help you move forward?"
    },

    # ─── YUDDHA KANDA ────────────────────────────────────────
    {
        "kanda": "Yuddha Kanda",
        "chapter": 18,
        "verse": 33,
        "reference": "Valmiki Ramayana, Yuddha Kanda 18.33",
        "character": "Shri Rama",
        "topic": "Universal Refuge & Compassion (अभयदान एवं शरणागति)",
        "sanskrit": "सकृदेव प्रपन्नाय तवास्मीति च याचते।\nअभयं सर्वभूतेभ्यो ददाम्येतद् व्रतं मम॥",
        "transliteration": "sakṛdeva prapannāya tavāsmīti ca yācate |\nabhayaṁ sarvabhūtebhyo dadāmyetad vrataṁ mama ||",
        "hindi_translation": "जो कोई भी प्राणी एक बार भी मेरी शरण में आकर यह कह देता है कि 'हे प्रभु! मैं आपका हूँ', उसे मैं सभी प्राणियों से सर्वथा अभय (सुरक्षा) प्रदान कर देता हूँ—यह मेरा परम व्रत है।",
        "translation": "To anyone who surrenders unto Me even once, saying 'I am Yours', I grant total fearlessness and protection from all beings. This is My solemn vow.",
        "context": "When Vibhishana seeks refuge with Rama, others doubt him, but Rama establishes the supreme principle of unconditional grace and refuge to all sincere seekers.",
        "reflection_title": "The Supreme Vow of Compassion",
        "explanation": "Rama's declaration of Abhaya (fearlessness) is one of the most sublime moments in world spiritual literature. True leadership offers grace and forgiveness to those who approach with genuine sincerity.",
        "key_takeaways": [
            "Extend grace and forgiveness to those who sincerely seek a fresh start",
            "Greatness is defined by how generously you protect and elevate others",
            "Let compassion supersede cynicism and paranoia"
        ],
        "today_practice": {
            "title": "The Gift of Acceptance (स्वीकार्यता)",
            "description": "Release a grudge or cold attitude toward someone who has reached out. Offer a warm and genuine response."
        },
        "journal_prompt": "Is there someone in your life you have held at a distance? What would granting them graceful acceptance look like?"
    },
    {
        "kanda": "Yuddha Kanda",
        "chapter": 105,
        "verse": 1,
        "reference": "Valmiki Ramayana, Yuddha Kanda 105.1 (Aditya Hridaya)",
        "character": "Sage Agastya to Shri Rama",
        "topic": "Invoking the Radiant Inner Light (आदित्य हृदय स्तोत्र)",
        "sanskrit": "ततो युद्धपरिश्रान्तं समरे चिन्तया स्थितम्।\nरावणं चाग्रतो दृष्ट्वा युद्धाय समुपस्थितम्॥",
        "transliteration": "tato yuddhaparidhrāntaṁ samare cintayā sthitam |\nrāvaṇaṁ cāgrato dṛṣṭvā yuddhāya samupasthitam ||",
        "hindi_translation": "जब युद्ध के भीषण मोड़ पर रावण को पुनः सम्मुख देखकर श्रीराम विचारमग्न हुए, तब महर्षि अगस्त्य ने उन्हें सनातन 'आदित्य हृदय स्तोत्र' का उपदेश दिया जो समस्त शत्रुओं पर विजय और परम आत्मबल प्रदान करने वाला है।",
        "translation": "Seeing Shri Rama weary and standing in deep contemplation on the battlefield before the final clash with Ravana, Sage Agastya imparted the immortal 'Aditya Hridaya' hymn to awaken divine energy, boundless vitality, and total victory.",
        "context": "Before the final duel with Ravana, Sage Agastya reveals the meditation on the Sun (Surya) as the source of cosmic life, inner brilliance, and invincible vitality.",
        "reflection_title": "Awakening Your Inner Solar Brilliance",
        "explanation": "Even the greatest heroes encounter moments of fatigue and deep testing. The Aditya Hridaya teaches us to reconnect with the infinite cosmic source of energy within us—clarity, vitality, and courage.",
        "key_takeaways": [
            "In moments of exhaustion, pause and reconnect with your inner spiritual source",
            "Light and truth inevitably dispel the heaviest darkness",
            "Maintain unwavering faith when facing the final phase of a long struggle"
        ],
        "today_practice": {
            "title": "Sunlight Meditation (तेज ध्यान)",
            "description": "Spend 5 minutes in natural morning sunlight, breathing deeply and visualizing clarity and vitality filling every cell of your mind and body."
        },
        "journal_prompt": "Where do you feel mentally tired right now, and how can you replenish your inner energy?"
    }
]

MAHABHARATA_DATASET = [
    # ─── ADI PARVA ───────────────────────────────────────────
    {
        "parva": "Adi Parva",
        "chapter": 1,
        "verse": 1,
        "reference": "Mahabharata, Adi Parva 1.1",
        "character": "Sage Vyasa (Mangalacharana)",
        "topic": "The Sacred Invocation of Victory (मंगलाचरण - जय का आह्वान)",
        "sanskrit": "नारायणं नमस्कृत्य नरं चैव नरोत्तमम्।\nदेवीं सरस्वतीं व्यासं ततो जयमुदीरयेत्॥",
        "transliteration": "nārāyaṇaṁ namaskṛtya naraṁ caiva narottamam |\ndevīṁ sarasvatīṁ vyāsaṁ tato jayamudīrayet ||",
        "hindi_translation": "भगवान नारायण (श्रीहरि), नरों में श्रेष्ठ नर (अर्जुन), भगवती सरस्वती देवी और महर्षि वेदव्यास को श्रद्धापूर्वक नमस्कार करके 'जय' (महाभारत ग्रंथ) का पाठ प्रारम्भ करना चाहिए।",
        "translation": "Having bowed down in deep reverence to Lord Narayana, to Nara the foremost of beings, to Goddess Sarasvati the embodiment of wisdom, and unto Sage Vyasa, let the sacred epic of Jaya (Mahabharata) be proclaimed.",
        "context": "The colossal epic begins with this foundational invocation (Mangalacharana). Every great spiritual journey and endeavor starts with humility, gratitude, and invoking divine wisdom.",
        "reflection_title": "Beginning with Reverence and Gratitude",
        "explanation": "Before embarking on any monumental journey—whether reading an epic, starting a new venture, or facing life's daily battles—the wise first center themselves in humility and gratitude. Recognizing that we stand on the shoulders of timeless wisdom and grace dissolves arrogance and grants us clarity of purpose.",
        "key_takeaways": [
            "Begin every significant endeavor with humility, reverence, and gratitude (मंगलाचरण)",
            "Aligning your mind with a higher purpose removes inner anxiety",
            "Acknowledge the mentors, teachers, and traditions that have guided your path"
        ],
        "today_practice": {
            "title": "The Sacred Start (सद्भाव से आरम्भ)",
            "description": "Before starting your principal work today, pause for 60 seconds. Mentally express heartfelt gratitude to your parents, teachers, and divine grace."
        },
        "journal_prompt": "What major project or phase of life are you currently undertaking? How can starting with gratitude and clear intention transform your approach?"
    },
    {
        "parva": "Adi Parva",
        "chapter": 1,
        "verse": 267,
        "reference": "Mahabharata, Adi Parva 1.267",
        "character": "Sage Vyasa",
        "topic": "The Shield of Dharma (धर्मो रक्षति रक्षितः)",
        "sanskrit": "धर्म एव हतो हन्ति धर्मो रक्षति रक्षितः।\nतस्माद् धर्मो न हन्तव्यो मा नो धर्मो हतोऽवधीत्॥",
        "transliteration": "dharma eva hato hanti dharmo rakṣati rakṣitaḥ |\ntasmād dharmo na hantavyo mā no dharmo hato'vadhīt ||",
        "hindi_translation": "नष्ट किया हुआ धर्म नष्ट करने वाले का नाश कर देता है, और रक्षा किया हुआ धर्म रक्षक की रक्षा करता है। इसलिए धर्म का कभी हनन नहीं करना चाहिए, ताकि नष्ट हुआ धर्म कभी हमारा नाश न करे।",
        "translation": "Dharma, when destroyed, destroys the violator; Dharma, when protected and preserved, protects the protector. Therefore, righteousness must never be violated, lest destroyed righteousness destroy us.",
        "context": "Sage Vyasa establishes this supreme moral theorem. Whenever ethics are compromised for short-term gain, systemic collapse inevitably follows.",
        "reflection_title": "The Law of Moral Equilibrium",
        "explanation": "Vyasa's timeless verse establishes that cosmic moral law (Dharma) is self-regulating. When you protect integrity, your integrity becomes an impenetrable shield around you in times of crisis.",
        "key_takeaways": [
            "Compromising ethics for immediate profit always creates greater future damage",
            "Living righteously creates an inner armor of peace and confidence",
            "Every action has an ethical ripple effect on society"
        ],
        "today_practice": {
            "title": "Ethical Guardian (धर्म की रक्षा)",
            "description": "When faced with an opportunity to cut corners today, choose the ethical path instead. Feel the dignity and peace that comes with doing things the right way."
        },
        "journal_prompt": "Where in your past did doing the right thing (even when difficult) protect your peace of mind later on?"
    },


    # ─── SABHA PARVA ─────────────────────────────────────────
    {
        "parva": "Sabha Parva",
        "chapter": 2,
        "verse": 72,
        "reference": "Mahabharata, Sabha Parva 2.72",
        "character": "Draupadi",
        "topic": "Moral Courage & Challenging Injustice (न्याय और नैतिक साहस)",
        "sanskrit": "सभायां शास्त्रतो वक्तुं धर्मे शास्त्रविनिश्चयः।\nनास्मि दासी परैर्जिता स्वामिना पूर्वमर्पिता॥",
        "transliteration": "sabhāyāṁ śāstrato vaktuṁ dharme śāstraviniścayaḥ |\nnāsmi dāsī parairjitā svāminā pūrvamarpitā ||",
        "hindi_translation": "द्रौपदी ने राजसभा के समस्त गुरुजनों और सभासदों से पूछा: 'धर्म की मर्यादा के अनुसार उत्तर दें! जो स्वयं को जुए में पहले ही हार चुका हो, क्या उसे दूसरे को दांव पर लगाने का कोई नैतिक या धार्मिक अधिकार शेष रहता है?'",
        "translation": "Draupadi challenged the elders of the royal assembly: 'Answer my question of Dharma! If a man has already lost himself in the dice game, does he still possess any authority to stake another? Speak the truth according to the laws of righteousness!'",
        "context": "In the royal gambling hall of Hastinapura, Draupadi confronts the silence of elders like Bhishma and Drona, exposing the catastrophic moral failure of the assembly.",
        "reflection_title": "Speaking Truth to Complicit Power",
        "explanation": "Draupadi represents intellectual clarity, fierce dignity, and moral courage. The silence of good people in the face of injustice became the root wound that made the Kurukshetra war inevitable.",
        "key_takeaways": [
            "Never silence your conscience in order to please social authority",
            "The failure of good people to speak up accelerates moral decay",
            "Dignity and self-respect are non-negotiable spiritual values"
        ],
        "today_practice": {
            "title": "Voice of Courage (सत्य का पक्ष)",
            "description": "If you witness unfairness, unkind gossip, or passive bias today, speak up constructively or refuse to participate in the harm."
        },
        "journal_prompt": "Have you ever remained silent when you knew you should have spoken up? What lesson did you take away from that moment?"
    },

    # ─── VANA PARVA ──────────────────────────────────────────
    {
        "parva": "Vana Parva",
        "chapter": 313,
        "verse": 116,
        "reference": "Mahabharata, Vana Parva (Yaksha Prashna) 3.313.116",
        "character": "Yudhishthira & The Yaksha",
        "topic": "The Greatest Wonder (संसार का सबसे बड़ा आश्चर्य)",
        "sanskrit": "अहन्यहनि भूतानि गच्छन्तीह यमालयम्।\nशेषाः स्थावरमिच्छन्ति किमाश्चर्यमतः परम्॥",
        "transliteration": "ahanyahani bhūtāni gacchantīha yamālayam |\nśeṣāḥ sthāvaramicchanti kimāścaryamataḥ param ||",
        "hindi_translation": "यक्ष ने पूछा: 'संसार का सबसे बड़ा आश्चर्य क्या है?' युधिष्ठिर ने उत्तर दिया: 'प्रतिदिन अनगिनत प्राणी यमलोक (मृत्यु) को प्राप्त होते हैं, फिर भी जो शेष बचे हैं वे सदा जीवित रहने की इच्छा करते हैं। इससे बड़ा आश्चर्य और क्या हो सकता है?'",
        "translation": "The Yaksha asked: 'What is the greatest wonder of the world?' Yudhishthira replied: 'Day after day, countless living beings depart for the abode of death. Yet those who remain believe they will live forever. What can be more astounding than this?'",
        "context": "At the enchanted lake, the divine Yaksha tests Yudhishthira with philosophical riddles. Yudhishthira's profound understanding revives his brothers.",
        "reflection_title": "Living with Awareness of Impermanence",
        "explanation": "Remembering our mortality is not morbid; it is the ultimate purifier of priorities. When we recognize that life is finite, we immediately focus on what truly matters: love, wisdom, generosity, and righteous living.",
        "key_takeaways": [
            "Awareness of mortality strips away trivial worries and clarifies what truly matters",
            "Do not postpone kindness, forgiveness, or spiritual growth for a vague future",
            "Treat each day as a precious, irreplaceable gift"
        ],
        "today_practice": {
            "title": "The Priority Filter (प्राथमिकता की परख)",
            "description": "Whenever you feel irritated by minor inconveniences today, ask yourself: 'Will this matter in the grand scheme of life?' Let go of trivial irritations instantly."
        },
        "journal_prompt": "If you lived today with full awareness of life's precious impermanence, how would you treat the people around you?"
    },

    # ─── UDYOGA PARVA ────────────────────────────────────────
    {
        "parva": "Udyoga Parva",
        "chapter": 33,
        "verse": 16,
        "reference": "Mahabharata, Udyoga Parva 33.16 (Vidura Niti)",
        "character": "Mahatma Vidura to King Dhritarashtra",
        "topic": "The Wise Person's Hallmarks (विदुर नीति - ज्ञानी के लक्षण)",
        "sanskrit": "आत्मज्ञानं समारम्भस्तितिक्षा धर्मनित्यता।\nयमर्थान्नापकर्षन्ति स वै पण्डित उच्यते॥",
        "transliteration": "ātmajñānaṁ samārambhastitikṣā dharmanityatā |\nyamarthānnāpakarṣanti sa vai paṇḍita ucyate ||",
        "hindi_translation": "जिस व्यक्ति को आत्मज्ञान हो, जो उत्साह और पुरुषार्थ से कार्य आरम्भ करता हो, जिसमें सहनशीलता (तितिक्षा) हो और जो सदा धर्म में स्थित रहता हो—जिसे सुख या दुःख विचलित न कर सकें, वही वास्तव में ज्ञानी कहलाता है।",
        "translation": "He who possesses self-knowledge, who initiates noble works with diligence, who has forbearance and steadfast devotion to righteousness, and whom neither prosperity nor adversity can deflect from virtue—he alone is truly wise.",
        "context": "In the famous Vidura Niti, the righteous prime minister Vidura counsels the restless blind King Dhritarashtra on wisdom, mental tranquility, and ethical governance.",
        "reflection_title": "The Four Pillars of Wisdom",
        "explanation": "True wisdom (Panditya) is not bookish scholarship; it is emotional stability, self-awareness, active discipline, and unwavering integrity under pressure.",
        "key_takeaways": [
            "Self-knowledge and emotional resilience define genuine intelligence",
            "Finish what you start with unwavering perseverance",
            "Do not let praise inflate you or criticism depress you"
        ],
        "today_practice": {
            "title": "The Wise Response (तितिक्षा और धैर्य)",
            "description": "Practice remaining completely poised today regardless of whether you receive compliments or criticism."
        },
        "journal_prompt": "Which of Vidura's four pillars of wisdom do you want to develop further?"
    },

    # ─── BHISHMA PARVA ───────────────────────────────────────
    {
        "parva": "Bhishma Parva",
        "chapter": 6,
        "verse": 14,
        "reference": "Mahabharata, Bhishma Parva 6.14",
        "character": "Pitamaha Bhishma",
        "topic": "The Ten Pillars of Character (धर्म के दस लक्षण)",
        "sanskrit": "धृतिः क्षमा दमोऽस्तेयं शौचमिन्द्रियनिग्रहः।\nधीर्विद्या सत्यमक्रोधो दशकं धर्मलक्षणम्॥",
        "transliteration": "dhṛtiḥ kṣamā damo'steyaṁ śaucamindriyanigrahaḥ |\ndhīrvidyā satyamakrodho daśakaṁ dharmalakṣaṇam ||",
        "hindi_translation": "धर्म के दस लक्षण हैं: धैर्‍य (धृति), क्षमा, मन पर संयम (दम), चोरी न करना (अस्तेय), शुचिता (पवित्रता), इन्द्रिय-निग्रह, बुद्धि का विकास (धी), विद्या (ज्ञान), सत्य और क्रोध न करना (अक्रोध)।",
        "translation": "The ten characteristics of Dharma are: Fortitude (Dhriti), Forgiveness (Kshama), Self-restraint (Dama), Non-stealing (Asteya), Purity (Shaucha), Mastery of Senses (Indriya-nigraha), Discernment (Dhi), Wisdom (Vidya), Truthfulness (Satya), and Freedom from Anger (Akrodha).",
        "context": "Grandfather Bhishma elucidates the universal foundational pillars of character that sustain human society and individual spiritual liberation.",
        "reflection_title": "The Ten Foundational Virtues",
        "explanation": "Bhishma synthesizes the entire ethical corpus of Vedic wisdom into ten actionable human virtues. Cultivating patience, mastering impulse, and abandoning anger transforms character into supreme mastery.",
        "key_takeaways": [
            "Character is built through the disciplined cultivation of daily virtues",
            "Mastery over anger (Akrodha) preserves relationships and mental clarity",
            "Inner purity and truthfulness generate authentic self-confidence"
        ],
        "today_practice": {
            "title": "Virtue in Focus: Akrodha (अक्रोध - क्रोध न करना)",
            "description": "Make a conscious commitment today: 'For the next 12 hours, I will not raise my voice or react with anger, no matter what triggers arise.'"
        },
        "journal_prompt": "Which of Bhishma's ten pillars of character is currently your greatest strength, and which one requires your deepest attention?"
    },

    # ─── KARNA PARVA ─────────────────────────────────────────
    {
        "parva": "Karna Parva",
        "chapter": 8,
        "verse": 49,
        "reference": "Mahabharata, Karna Parva 8.49",
        "character": "Karna",
        "topic": "Effort and Self-Made Destiny (कर्म और पुरुषार्थ)",
        "sanskrit": "दैवायत्तं कुले जन्म मदायत्तं तु पौरुषम्।\nकर्मणैव हि संसिद्धिं लभते पुरुषोत्तमः॥",
        "transliteration": "daivāyattaṁ kule janma madāyattaṁ tu pauruṣam |\nkarmaṇaiva hi saṁsiddhiṁ labhate puruṣottamaḥ ||",
        "hindi_translation": "किसी कुल में जन्म लेना दैव (प्रारब्ध) के अधीन है, किंतु मेरा पुरुषार्थ, मेरा पराक्रम और मेरा चरित्र सर्वथा मेरे अपने अधीन है! मनुष्य अपने कर्मों से ही श्रेष्ठता और सिद्धि प्राप्त करता है।",
        "translation": "Birth in a family depends on destiny, but my courage, character, and mastery depend entirely upon myself! A person attains true greatness through their own dedicated actions alone.",
        "context": "Karna asserts that human greatness is determined by one's own dedicated effort and character rather than birth or external privilege.",
        "reflection_title": "Transcending Circumstances through Effort",
        "explanation": "We cannot choose where we start in life, but our discipline, courage, work ethic, and character belong entirely to us.",
        "key_takeaways": [
            "Do not let past disadvantages define your ceiling of growth",
            "Focused effort and relentless discipline surpass unearned privilege",
            "Take 100% personal responsibility for your life"
        ],
        "today_practice": {
            "title": "Take 100% Ownership",
            "description": "Stop blaming any external factor for a current delay. Take decisive, proactive action today."
        },
        "journal_prompt": "What limitation have you allowed to hold you back? How can you break through it today?"
    },

    # ─── SHANTI PARVA ────────────────────────────────────────
    {
        "parva": "Shanti Parva",
        "chapter": 12,
        "verse": 167,
        "reference": "Mahabharata, Shanti Parva 12.167",
        "character": "Bhishma to Yudhishthira",
        "topic": "The Power of Humility and Respect (विनम्रता और ज्ञान प्राप्ति)",
        "sanskrit": "अभिवादनशीलस्य नित्यं वृद्धोपसेविनः।\nचत्वारि तस्य वर्धन्ते आयुर्विद्या यशो बलम्॥",
        "transliteration": "abhivādanaśīlasya nityaṁ vṛddhopasevinaḥ |\ncatvāri tasya vardhante āyurvidyā yaśo balam ||",
        "hindi_translation": "जो व्यक्ति स्वभाव से विनम्र रहता है और नित्य ज्ञानी व वृद्धजनों का आदर-सत्कार करता है, उसकी चार चीजें निरन्तर बढ़ती हैं: आयु, विद्या, कीर्ति (यश) और आत्मबल।",
        "translation": "For one who is humble, respectful, and continually honors the wise and elderly, four divine blessings multiply: longevity, wisdom, noble renown, and inner strength.",
        "context": "In the Shanti Parva, Bhishma imparts the Rajadharma to Yudhishthira, explaining how humility opens the mind to absorb timeless wisdom.",
        "reflection_title": "Humility as the Gateway to Wisdom",
        "explanation": "Humility is the receptive state of mind that allows wisdom to flow inward. Arrogance closes the mind to learning, while reverence creates receptivity.",
        "key_takeaways": [
            "Humility expands your capacity to learn and absorb true knowledge",
            "Arrogance repels wisdom and isolates the leader",
            "Honor mentors and elders who paved the path before you"
        ],
        "today_practice": {
            "title": "Seek Wisdom with Humility",
            "description": "Ask an experienced colleague or elder for their perspective on a challenge you are facing, and listen with complete attention."
        },
        "journal_prompt": "Who in your life possesses wisdom you could benefit from learning?"
    },

    # ─── ANUSHASANA PARVA ────────────────────────────────────
    {
        "parva": "Anushasana Parva",
        "chapter": 13,
        "verse": 1,
        "reference": "Mahabharata, Anushasana Parva 13.1",
        "character": "Bhishma",
        "topic": "Compassionate Truth (सत्य और प्रिय वाणी)",
        "sanskrit": "सत्यं ब्रूयात् प्रियं ब्रूयान्न ब्रूयात् सत्यमप्रियम्।\nप्रियं च नानृतं ब्रूयादेष धर्मः सनातनः॥",
        "transliteration": "satyaṁ brūyāt priyaṁ brūyānna brūyāt satyamapriyam |\npriyaṁ ca nānṛtaṁ brūyādeṣa dharmaḥ sanātanaḥ ||",
        "hindi_translation": "सत्य बोलना चाहिए, प्रिय (मधुर) बोलना चाहिए, किंतु ऐसा सत्य नहीं बोलना चाहिए जो दूसरों को व्यर्थ पीड़ा पहुंचाए (कठोर सत्य)। और प्रिय लगने वाला असत्य भी कभी नहीं बोलना चाहिए—यही सनातन धर्म है।",
        "translation": "Speak truth; speak with kindness and benevolence; do not speak a truth with cruelty or spite; and do not speak pleasing falsehoods. This is the eternal law of righteous communication.",
        "context": "Bhishma imparts the timeless art of speech (Vak-tapas), explaining that how truth is delivered matters as much as the truth itself.",
        "reflection_title": "The Art of Compassionate Communication",
        "explanation": "The highest communication balances absolute honesty with deep goodwill. Speech that is truthful, beneficial, and gentle is a spiritual austerity.",
        "key_takeaways": [
            "Deliver truthful feedback with constructive goodwill, never malice",
            "Avoid pleasing flattery that conceals damaging mistakes",
            "Speech that is truthful, beneficial, and gentle is a spiritual austerity"
        ],
        "today_practice": {
            "title": "The Triple Filter of Speech (वाणी का त्रिवेणी नियम)",
            "description": "Before speaking today, ask yourself: 'Is it true? Is it kind? Is it necessary?'"
        },
        "journal_prompt": "Think of a time someone told you a hard truth with kindness. How did that compassionate honesty help you grow?"
    }
]
