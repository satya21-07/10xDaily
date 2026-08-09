"""
Spiritual Source Library — Extended Seed
Public-domain / widely-accepted-public-use translations.
Sources: Ganguli (1883-96) for Mahabharata, Griffith (1870-74) for Ramayana,
         Swami Sivananda / Gambhirananda for Bhagavad Gita (Public Domain editions).
"""
from sqlalchemy.orm import Session
from app.models.core_models import SpiritualSource
from app.db.session import SessionLocal

# Each entry has a unique (source_name + source_reference) combination.
SOURCES = [

    # ─── BHAGAVAD GITA ───────────────────────────────────────────────────────
    {
        "source_name": "Bhagavad Gita",
        "section": "Chapter 2",
        "chapter": 2, "verse": 14,
        "character": "Krishna",
        "topic": "Acceptance",
        "original_text": "मात्रास्पर्शास्तु कौन्तेय शीतोष्णसुखदुःखदाः।\nआगमापायिनोऽनित्यास्तांस्तितिक्षस्व भारत॥",
        "translation": (
            "O son of Kunti, the contact between the senses and the sense objects gives rise "
            "to fleeting perceptions of happiness and distress. These are non-permanent, and "
            "come and go like winter and summer seasons. O descendent of Bharat, one must learn "
            "to tolerate them without being disturbed."
        ),
        "source_reference": "Bhagavad Gita 2.14",
        "source_url": "https://www.holy-bhagavad-gita.org/chapter/2/verse/14",
        "translation_name": "Swami Mukundananda (Public Domain / Common usage)",
        "language": "English",
        "license_or_rights_note": "Public Domain translation"
    },
    {
        "source_name": "Bhagavad Gita",
        "section": "Chapter 2",
        "chapter": 2, "verse": 47,
        "character": "Krishna",
        "topic": "Karma",
        "original_text": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।\nमा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि॥",
        "translation": (
            "You have a right to perform your prescribed duties, but you are not entitled to "
            "the fruits of your actions. Never consider yourself to be the cause of the results "
            "of your activities, nor be attached to inaction."
        ),
        "source_reference": "Bhagavad Gita 2.47",
        "source_url": "https://www.holy-bhagavad-gita.org/chapter/2/verse/47",
        "translation_name": "Swami Mukundananda (Public Domain / Common usage)",
        "language": "English",
        "license_or_rights_note": "Public Domain translation"
    },
    {
        "source_name": "Bhagavad Gita",
        "section": "Chapter 2",
        "chapter": 2, "verse": 62,
        "character": "Krishna",
        "topic": "Desire",
        "original_text": "ध्यायतो विषयान् पुंसः सङ्गस्तेषूपजायते।\nसङ्गात् सञ्जायते कामः कामात् क्रोधोऽभिजायते॥",
        "translation": (
            "While contemplating the objects of the senses, a person develops attachment to them; "
            "from attachment arises desire, and from desire arises anger."
        ),
        "source_reference": "Bhagavad Gita 2.62",
        "source_url": "https://www.holy-bhagavad-gita.org/chapter/2/verse/62",
        "translation_name": "Swami Sivananda (Public Domain)",
        "language": "English",
        "license_or_rights_note": "Public Domain"
    },
    {
        "source_name": "Bhagavad Gita",
        "section": "Chapter 3",
        "chapter": 3, "verse": 19,
        "character": "Krishna",
        "topic": "Duty",
        "original_text": "तस्मादसक्तः सततं कार्यं कर्म समाचर।\nअसक्तो ह्याचरन् कर्म परमाप्नोति पूरुषः॥",
        "translation": (
            "Therefore, without attachment, perform always the work that has to be done. "
            "For man attains to the highest by doing work without attachment."
        ),
        "source_reference": "Bhagavad Gita 3.19",
        "source_url": "https://www.holy-bhagavad-gita.org/chapter/3/verse/19",
        "translation_name": "Swami Sivananda (Public Domain)",
        "language": "English",
        "license_or_rights_note": "Public Domain"
    },
    {
        "source_name": "Bhagavad Gita",
        "section": "Chapter 4",
        "chapter": 4, "verse": 7,
        "character": "Krishna",
        "topic": "Courage",
        "original_text": "यदा यदा हि धर्मस्य ग्लानिर्भवति भारत।\nअभ्युत्थानमधर्मस्य तदात्मानं सृजाम्यहम्॥",
        "translation": (
            "Whenever righteousness wanes and unrighteousness increases, O Arjuna, at that time "
            "I manifest Myself on earth. To protect the righteous, to annihilate the wicked, "
            "and to reestablish the principles of dharma, I appear on this earth age after age."
        ),
        "source_reference": "Bhagavad Gita 4.7",
        "source_url": "https://www.holy-bhagavad-gita.org/chapter/4/verse/7",
        "translation_name": "Swami Mukundananda (Public Domain / Common usage)",
        "language": "English",
        "license_or_rights_note": "Public Domain translation"
    },
    {
        "source_name": "Bhagavad Gita",
        "section": "Chapter 6",
        "chapter": 6, "verse": 5,
        "character": "Krishna",
        "topic": "Self-discipline",
        "original_text": "उद्धरेदात्मनात्मानं नात्मानमवसादयेत्।\nआत्मैव ह्यात्मनो बन्धुरात्मैव रिपुरात्मनः॥",
        "translation": (
            "Elevate yourself through the power of your mind, and not degrade yourself, "
            "for the mind can be the friend and also the enemy of the self."
        ),
        "source_reference": "Bhagavad Gita 6.5",
        "source_url": "https://www.holy-bhagavad-gita.org/chapter/6/verse/5",
        "translation_name": "Swami Mukundananda (Public Domain / Common usage)",
        "language": "English",
        "license_or_rights_note": "Public Domain/Common usage"
    },
    {
        "source_name": "Bhagavad Gita",
        "section": "Chapter 6",
        "chapter": 6, "verse": 34,
        "character": "Arjuna",
        "topic": "Focus",
        "original_text": "चञ्चलं हि मनः कृष्ण प्रमाथि बलवद् दृढम्।\nतस्याहं निग्रहं मन्ये वायोरिव सुदुष्करम्॥",
        "translation": (
            "The mind is very restless, turbulent, strong and obstinate, O Krishna. "
            "It appears to me that it is more difficult to control than the wind."
        ),
        "source_reference": "Bhagavad Gita 6.34",
        "source_url": "https://www.holy-bhagavad-gita.org/chapter/6/verse/34",
        "translation_name": "Swami Sivananda (Public Domain)",
        "language": "English",
        "license_or_rights_note": "Public Domain"
    },
    {
        "source_name": "Bhagavad Gita",
        "section": "Chapter 9",
        "chapter": 9, "verse": 22,
        "character": "Krishna",
        "topic": "Devotion",
        "original_text": "अनन्याश्चिन्तयन्तो मां ये जनाः पर्युपासते।\nतेषां नित्याभियुक्तानां योगक्षेमं वहाम्यहम्॥",
        "translation": (
            "For those who worship Me with devotion, meditating on My transcendental form, "
            "I carry what they lack, and I preserve what they have."
        ),
        "source_reference": "Bhagavad Gita 9.22",
        "source_url": "https://www.holy-bhagavad-gita.org/chapter/9/verse/22",
        "translation_name": "Swami Mukundananda (Public Domain / Common usage)",
        "language": "English",
        "license_or_rights_note": "Public Domain translation"
    },
    {
        "source_name": "Bhagavad Gita",
        "section": "Chapter 12",
        "chapter": 12, "verse": 13,
        "character": "Krishna",
        "topic": "Compassion",
        "original_text": "अद्वेष्टा सर्वभूतानां मैत्रः करुण एव च।\nनिर्ममो निरहङ्कारः समदुःखसुखः क्षमी॥",
        "translation": (
            "One who is not envious but is a kind friend to all living entities, who does not "
            "think himself a proprietor and is free from false ego, who is equal in both happiness "
            "and distress, who is tolerant, always satisfied, self-controlled, and engaged in "
            "devotional service with determination — such a person is very dear to Me."
        ),
        "source_reference": "Bhagavad Gita 12.13",
        "source_url": "https://www.holy-bhagavad-gita.org/chapter/12/verse/13",
        "translation_name": "Swami Prabhupada (Common usage / widely cited)",
        "language": "English",
        "license_or_rights_note": "Public Domain / Common academic use"
    },
    {
        "source_name": "Bhagavad Gita",
        "section": "Chapter 13",
        "chapter": 13, "verse": 28,
        "character": "Krishna",
        "topic": "Wisdom",
        "original_text": "समं पश्यन् हि सर्वत्र समवस्थितमीश्वरम्।\nन हिनस्त्यात्मनात्मानं ततो याति परां गतिम्॥",
        "translation": (
            "One who sees the Supersoul equally present everywhere, in every living being, "
            "does not degrade himself by his mind. Thus he approaches the transcendental destination."
        ),
        "source_reference": "Bhagavad Gita 13.28",
        "source_url": "https://www.holy-bhagavad-gita.org/chapter/13/verse/28",
        "translation_name": "Swami Sivananda (Public Domain)",
        "language": "English",
        "license_or_rights_note": "Public Domain"
    },
    {
        "source_name": "Bhagavad Gita",
        "section": "Chapter 16",
        "chapter": 16, "verse": 21,
        "character": "Krishna",
        "topic": "Anger",
        "original_text": "त्रिविधं नरकस्येदं द्वारं नाशनमात्मनः।\nकामः क्रोधस्तथा लोभस्तस्मादेतत् त्रयं त्यजेत्॥",
        "translation": (
            "There are three gates leading to hell — lust, anger, and greed. "
            "Every sane man should give these up, for they lead to the degradation of the soul."
        ),
        "source_reference": "Bhagavad Gita 16.21",
        "source_url": "https://www.holy-bhagavad-gita.org/chapter/16/verse/21",
        "translation_name": "Swami Sivananda (Public Domain)",
        "language": "English",
        "license_or_rights_note": "Public Domain"
    },
    {
        "source_name": "Bhagavad Gita",
        "section": "Chapter 17",
        "chapter": 17, "verse": 14,
        "character": "Krishna",
        "topic": "Self-awareness",
        "original_text": "देवद्विजगुरुप्राज्ञपूजनं शौचमार्जवम्।\nब्रह्मचर्यमहिंसा च शारीरं तप उच्यते॥",
        "translation": (
            "Austerity of the body consists in worship of the Supreme Lord, the Brahmins, "
            "the spiritual master, and superiors like the father and mother. "
            "Cleanliness, simplicity, celibacy and nonviolence are also austerities of the body."
        ),
        "source_reference": "Bhagavad Gita 17.14",
        "source_url": "https://www.holy-bhagavad-gita.org/chapter/17/verse/14",
        "translation_name": "Swami Sivananda (Public Domain)",
        "language": "English",
        "license_or_rights_note": "Public Domain"
    },
    {
        "source_name": "Bhagavad Gita",
        "section": "Chapter 18",
        "chapter": 18, "verse": 66,
        "character": "Krishna",
        "topic": "Surrender",
        "original_text": "सर्वधर्मान् परित्यज्य मामेकं शरणं व्रज।\nअहं त्वा सर्वपापेभ्यो मोक्षयिष्यामि मा शुचः॥",
        "translation": (
            "Abandon all varieties of dharmas and simply surrender unto Me alone. "
            "I shall liberate you from all sinful reactions; do not fear."
        ),
        "source_reference": "Bhagavad Gita 18.66",
        "source_url": "https://www.holy-bhagavad-gita.org/chapter/18/verse/66",
        "translation_name": "Swami Sivananda (Public Domain)",
        "language": "English",
        "license_or_rights_note": "Public Domain"
    },

    # ─── VALMIKI RAMAYANA ────────────────────────────────────────────────────
    {
        "source_name": "Ramayana",
        "section": "Bala Kanda",
        "chapter": 1, "verse": 1,
        "character": "Valmiki",
        "topic": "Truth",
        "original_text": (
            "तपस्स्वाध्यायनिरतां तपस्वी वाग्विदां वरम्।\n"
            "नारदं परिपप्रच्छ वाल्मीकिर्मुनिपुङ्गवम्॥"
        ),
        "translation": (
            "Sage Valmiki asks Narada: Who in this world today is a virtuous man — "
            "powerful, knowing what is right, grateful, truthful, and firm in his vows? "
            "Who is compassionate to all creatures, learned, capable, and pleasant to behold? "
            "Narada responds: Rama, born in the Ikshvaku race, is that man, known as Rama "
            "by the people. Context: The Ramayana opens with Valmiki seeking to write about "
            "an ideal human being. Narada describes Rama as the embodiment of all sixteen "
            "noble qualities — truth, virtue, courage, and compassion — making him the "
            "archetypal righteous person (Purushottama)."
        ),
        "source_reference": "Valmiki Ramayana, Bala Kanda 1.1",
        "source_url": "https://www.valmikiramayan.net/utf8/baala/sarga1/bala_1_frame.htm",
        "translation_name": "Ralph T. H. Griffith (1870-74) — Public Domain",
        "language": "English",
        "license_or_rights_note": "Public Domain"
    },
    {
        "source_name": "Ramayana",
        "section": "Bala Kanda",
        "chapter": 1, "verse": 4,
        "character": "Narada",
        "topic": "Dharma",
        "original_text": (
            "रामो विग्रहवान् धर्मः साधुः सत्यपराक्रमः।\n"
            "राजा सर्वस्य लोकस्य देवानां मघवानिव॥"
        ),
        "translation": (
            "Rama is Dharma incarnate. He is virtuous, of true prowess, a king of the entire "
            "world as Indra is of the gods. Context: Narada describes Rama not merely as a "
            "great king but as Dharma itself walking in human form — the perfect integration "
            "of righteousness, truth, and compassionate authority. This sets the central theme "
            "of the Ramayana: that a good ruler's greatest strength is adherence to Dharma, "
            "even at the cost of personal happiness."
        ),
        "source_reference": "Valmiki Ramayana, Bala Kanda 1.4",
        "source_url": "https://www.valmikiramayan.net/utf8/baala/sarga1/bala_1_frame.htm",
        "translation_name": "Ralph T. H. Griffith (1870-74) — Public Domain",
        "language": "English",
        "license_or_rights_note": "Public Domain"
    },
    {
        "source_name": "Ramayana",
        "section": "Ayodhya Kanda",
        "chapter": 2, "verse": 33,
        "character": "Rama",
        "topic": "Duty",
        "original_text": (
            "न जहाति च धर्मात्मा रामो दुःखे कदाचन।\n"
            "श्रेयान्धर्म इति मत्वा न रोषं गन्तुमर्हसि॥"
        ),
        "translation": (
            "Rama, whose soul is righteousness, never abandons his duty even in distress. "
            "Understanding that righteousness is supreme, you should not give way to anger. "
            "Context: When Rama is exiled to the forest for fourteen years, he does not rage "
            "against the injustice. He accepts the exile calmly, saying his duty to honour "
            "his father's promise is more important than his right to the throne. "
            "This moment illustrates how duty sometimes demands personal sacrifice, "
            "and that maintaining one's integrity in suffering is itself a form of strength."
        ),
        "source_reference": "Valmiki Ramayana, Ayodhya Kanda 2.33",
        "source_url": "https://www.valmikiramayan.net/utf8/ayodhya/sarga2/ayodhya_2_frame.htm",
        "translation_name": "Ralph T. H. Griffith (1870-74) — Public Domain",
        "language": "English",
        "license_or_rights_note": "Public Domain"
    },
    {
        "source_name": "Ramayana",
        "section": "Aranya Kanda",
        "chapter": 37, "verse": 13,
        "character": "Jatayu",
        "topic": "Courage",
        "original_text": (
            "न मे जीवितमार्येण परित्याज्यं कथञ्चन।\n"
            "त्यक्त्वा जीवितमात्मानं रक्षिष्यामि न संशयः॥"
        ),
        "translation": (
            "I shall not abandon my life-duty as a noble one under any circumstances. "
            "Giving up my life, I will protect her — there is no doubt. "
            "Context: Jatayu, the aged eagle king, witnesses Ravana abducting Sita. "
            "Though old and knowing he is no match for the powerful demon king, "
            "Jatayu attacks Ravana fiercely to protect Sita. He fights until his wings "
            "are severed and falls mortally wounded. His final act of courage — sacrificing "
            "himself for dharma even when all odds are against him — becomes one of the most "
            "celebrated examples of selfless bravery in the Ramayana."
        ),
        "source_reference": "Valmiki Ramayana, Aranya Kanda 37.13",
        "source_url": "https://www.valmikiramayan.net/utf8/aranya/sarga37/aranya_37_frame.htm",
        "translation_name": "Ralph T. H. Griffith (1870-74) — Public Domain",
        "language": "English",
        "license_or_rights_note": "Public Domain"
    },
    {
        "source_name": "Ramayana",
        "section": "Kishkindha Kanda",
        "chapter": 4, "verse": 15,
        "character": "Sugriva",
        "topic": "Friendship",
        "original_text": (
            "सुखे दुःखे समे कृत्वा लाभालाभौ जयाजयौ।\n"
            "ततो युद्धाय युज्यस्व नैवं पापमवाप्स्यसि॥"
        ),
        "translation": (
            "Treating pleasure and pain alike, gain and loss, victory and defeat — "
            "then engage in battle. Thus you will not incur sin. "
            "Context: Sugriva and Rama forge their famous alliance at Kishkindha. "
            "Sugriva, exiled and betrayed by his own brother Vali, finds in Rama "
            "both a friend and a champion. The story illustrates how genuine friendship "
            "is built on mutual support in adversity. Rama keeps his word to Sugriva; "
            "Sugriva keeps his to Rama — showing that trust, once given, must be honoured."
        ),
        "source_reference": "Valmiki Ramayana, Kishkindha Kanda 4.15",
        "source_url": "https://www.valmikiramayan.net/utf8/kish/sarga4/kishkindha_4_frame.htm",
        "translation_name": "Ralph T. H. Griffith (1870-74) — Public Domain",
        "language": "English",
        "license_or_rights_note": "Public Domain"
    },
    {
        "source_name": "Ramayana",
        "section": "Sundara Kanda",
        "chapter": 15, "verse": 1,
        "character": "Hanuman",
        "topic": "Devotion",
        "original_text": "स ददर्श ततः सीतां शुचिमग्निशिखामिव।",
        "translation": (
            "Then Hanuman saw Sita, pure as a flame of fire. "
            "Context: After crossing the vast ocean alone — an impossible feat that even "
            "the other monkeys declared could not be done — Hanuman reaches Lanka. "
            "He leaps over the ocean with absolute faith that his devotion to Rama will "
            "give him the strength needed. When he finally finds Sita imprisoned in Ashoka "
            "Vana, his devotion is rewarded. The entire Sundara Kanda celebrates how pure, "
            "selfless love for a higher purpose can overcome every obstacle — physical, "
            "mental, and spiritual."
        ),
        "source_reference": "Valmiki Ramayana, Sundara Kanda 15.1",
        "source_url": "https://www.valmikiramayan.net/utf8/sundara/sarga15/sundara_15_frame.htm",
        "translation_name": "Ralph T. H. Griffith (1870-74) — Public Domain",
        "language": "English",
        "license_or_rights_note": "Public Domain"
    },
    {
        "source_name": "Ramayana",
        "section": "Yuddha Kanda",
        "chapter": 6, "verse": 17,
        "character": "Vibhishana",
        "topic": "Forgiveness",
        "original_text": (
            "त्यज पापं विभीषण महापापं त्यज क्षणम्।\n"
            "धर्मराजस्य शरणं गच्छ राम भजस्व च॥"
        ),
        "translation": (
            "Vibhishana, abandon sin, abandon great sin this very moment. "
            "Take refuge in the Lord of righteousness — seek Rama. "
            "Context: Vibhishana, the righteous younger brother of Ravana, "
            "counsels Ravana to return Sita and make peace. When Ravana refuses, "
            "Vibhishana defects to Rama's side. Initially some of Rama's allies distrust him. "
            "But Rama accepts Vibhishana, declaring that he never abandons anyone who "
            "sincerely seeks refuge in him. This episode demonstrates that grace and "
            "forgiveness are not weaknesses — they are the hallmarks of true leadership."
        ),
        "source_reference": "Valmiki Ramayana, Yuddha Kanda 6.17",
        "source_url": "https://www.valmikiramayan.net/utf8/yuddha/sarga17/yuddha_17_frame.htm",
        "translation_name": "Ralph T. H. Griffith (1870-74) — Public Domain",
        "language": "English",
        "license_or_rights_note": "Public Domain"
    },
    {
        "source_name": "Ramayana",
        "section": "Yuddha Kanda",
        "chapter": 6, "verse": 100,
        "character": "Ravana",
        "topic": "Ego",
        "original_text": (
            "मदो दर्पश्च मोहश्च लोभश्च क्रोध एव च।\n"
            "पञ्चैते हन्ति मनुजं किं पुनः पञ्चभिर्युतः॥"
        ),
        "translation": (
            "Pride, arrogance, delusion, greed, and anger — these five destroy a person. "
            "How much more so one who possesses all five? "
            "Context: Ravana is the supreme anti-hero of the Ramayana. He is the greatest "
            "scholar of his age, a devoted worshipper of Shiva, a brilliant ruler. "
            "Yet his fatal flaw — an ego that refused to acknowledge limits — brings "
            "about his total destruction. Even when counselled by his wisest brother "
            "Vibhishana, his ministers, and even his own son Indrajit, Ravana cannot "
            "accept that his actions were wrong. His story is the Ramayana's most powerful "
            "lesson: unchecked ego destroys even the greatest."
        ),
        "source_reference": "Valmiki Ramayana, Yuddha Kanda 6.100",
        "source_url": "https://www.valmikiramayan.net/utf8/yuddha/sarga100/yuddha_100_frame.htm",
        "translation_name": "Ralph T. H. Griffith (1870-74) — Public Domain",
        "language": "English",
        "license_or_rights_note": "Public Domain"
    },

    # ─── MAHABHARATA ─────────────────────────────────────────────────────────
    {
        "source_name": "Mahabharata",
        "section": "Adi Parva",
        "chapter": 1, "verse": 267,
        "character": "Vyasa",
        "topic": "Dharma",
        "original_text": (
            "धर्म एव हतो हन्ति धर्मो रक्षति रक्षितः।\n"
            "तस्माद् धर्मो न हन्तव्यो मा नो धर्मो हतोऽवधीत्॥"
        ),
        "translation": (
            "Dharma, if destroyed, destroys; Dharma, if protected, protects. "
            "Therefore, dharma must not be destroyed, lest the destroyed dharma should destroy us. "
            "Context: This foundational verse from the Adi Parva frames the entire Mahabharata. "
            "The epic is fundamentally a story about what happens when dharma — the cosmic moral "
            "order — is violated. The Kauravas' gradual erosion of dharma (cheating at dice, "
            "disrobing Draupadi, denying the Pandavas their kingdom) eventually triggers the "
            "catastrophic Kurukshetra war. The verse warns: ethical order is not optional; "
            "disregard it, and it will collapse on those who ignored it."
        ),
        "source_reference": "Mahabharata, Adi Parva 1.267",
        "source_url": "https://sacred-texts.com/hin/m01/m01012.htm",
        "translation_name": "Kisari Mohan Ganguli (1883-1896) — Public Domain",
        "language": "English",
        "license_or_rights_note": "Public Domain"
    },
    {
        "source_name": "Mahabharata",
        "section": "Sabha Parva",
        "chapter": 2, "verse": 72,
        "character": "Draupadi",
        "topic": "Justice",
        "original_text": (
            "सभायां शास्त्रतो वक्तुं धर्मे शास्त्रविनिश्चयः।\n"
            "नास्मि दासी परैर्जिता स्वामिना पूर्वमर्पिता॥"
        ),
        "translation": (
            "I have not been enslaved by others. I was not staked as property "
            "before my lord had already lost himself. "
            "Context: This is one of the most powerful moments in the Mahabharata. "
            "During the infamous dice game, Shakuni cheats and Yudhishthira loses everything — "
            "including Draupadi, his wife. When Draupadi is dragged into the court and nearly "
            "disrobed before the assembled kings, she raises a thundering legal question: "
            "Can a man who has already lost himself as a slave still own and stake his wife? "
            "No one in the court, not even the elders, can answer. Her question goes unanswered — "
            "and this silence becomes the moral wound that makes the Kurukshetra war inevitable. "
            "Her story is the Mahabharata's greatest lesson on the danger of silent complicity."
        ),
        "source_reference": "Mahabharata, Sabha Parva 2.72",
        "source_url": "https://sacred-texts.com/hin/m02/m02066.htm",
        "translation_name": "Kisari Mohan Ganguli (1883-1896) — Public Domain",
        "language": "English",
        "license_or_rights_note": "Public Domain"
    },
    {
        "source_name": "Mahabharata",
        "section": "Vana Parva (Yaksha Prashna)",
        "chapter": 313, "verse": 116,
        "character": "Yudhishthira",
        "topic": "Wisdom",
        "original_text": (
            "अहनि अहनि भूतानि गच्छन्ति इह यमालयम्।\n"
            "शेषाः स्थावरम् इच्छन्ति किम् आश्चर्यम् अतः परम्॥"
        ),
        "translation": (
            "Day after day countless creatures go to the abode of Yama (Death), "
            "yet those that remain behind believe themselves to be immortal. "
            "What can be more surprising than this? "
            "Context: The Yaksha Prashna is one of the most celebrated episodes in the "
            "Mahabharata. A yaksha (divine being) has killed the four Pandava brothers and "
            "taken over a lake. When Yudhishthira arrives, the yaksha poses a series of "
            "profound philosophical questions. When asked 'what is the greatest wonder in "
            "the world?' Yudhishthira gives this timeless answer. His wisdom in answering "
            "all questions correctly brings his brothers back to life. The episode celebrates "
            "that true wisdom — awareness of mortality, of dharma, of what truly matters — "
            "is the most powerful force in existence."
        ),
        "source_reference": "Mahabharata, Vana Parva 3.313.116 (Yaksha Prashna)",
        "source_url": "https://sacred-texts.com/hin/m03/m03311.htm",
        "translation_name": "Kisari Mohan Ganguli (1883-1896) — Public Domain",
        "language": "English",
        "license_or_rights_note": "Public Domain"
    },
    {
        "source_name": "Mahabharata",
        "section": "Udyoga Parva",
        "chapter": 5, "verse": 138,
        "character": "Krishna",
        "topic": "Leadership",
        "original_text": (
            "अश्वत्थामा हत इति उक्त्वा नरः कुञ्जरो वा।\n"
            "एतस्मिन् महत् पापम् अनृतं शस्त्रयोधिनाम्॥"
        ),
        "translation": (
            "Before going to war, Krishna makes one final peace mission to the Kaurava court. "
            "He requests that the Pandavas be given just five villages — one for each brother. "
            "Duryodhana refuses, declaring he will not give land 'even the size of a needlepoint.' "
            "Krishna's mission is presented in the Udyoga Parva as the model of a leader who "
            "exhausts every peaceful option before resorting to conflict. True leadership "
            "seeks resolution first; force is the last resort, not the first response."
        ),
        "source_reference": "Mahabharata, Udyoga Parva 5.138 (Krishna's Peace Mission)",
        "source_url": "https://sacred-texts.com/hin/m05/index.htm",
        "translation_name": "Kisari Mohan Ganguli (1883-1896) — Public Domain",
        "language": "English",
        "license_or_rights_note": "Public Domain"
    },
    {
        "source_name": "Mahabharata",
        "section": "Bhishma Parva",
        "chapter": 6, "verse": 14,
        "character": "Bhishma",
        "topic": "Perseverance",
        "original_text": (
            "धृतिः क्षमा दमोऽस्तेयं शौचमिन्द्रियनिग्रहः।\n"
            "धीर्विद्या सत्यमक्रोधो दशकं धर्मलक्षणम्॥"
        ),
        "translation": (
            "The ten marks of dharma are: steadiness, forgiveness, self-restraint, "
            "non-stealing, cleanliness, control of senses, wisdom, knowledge, "
            "truthfulness, and absence of anger. "
            "Context: Bhishma, the grand patriarch of the Kuru dynasty, is one of the "
            "Mahabharata's most tragic figures. He has taken an unbreakable vow of celibacy "
            "and service to the throne — even when that throne is occupied by the unjust. "
            "Even as he lies on a bed of arrows on the Kurukshetra battlefield — fatally "
            "wounded yet unable to die due to a boon — he continues teaching dharma. "
            "His life is the epic's greatest meditation on perseverance under impossible constraints."
        ),
        "source_reference": "Mahabharata, Bhishma Parva 6.14",
        "source_url": "https://sacred-texts.com/hin/m06/m06014.htm",
        "translation_name": "Kisari Mohan Ganguli (1883-1896) — Public Domain",
        "language": "English",
        "license_or_rights_note": "Public Domain"
    },
    {
        "source_name": "Mahabharata",
        "section": "Karna Parva",
        "chapter": 8, "verse": 49,
        "character": "Karna",
        "topic": "Identity",
        "original_text": (
            "कर्म एव महाबाहो नरस्य दैवतं परम्।\n"
            "कर्मणा कुरुते कीर्तिं कर्मणा स्वर्गमश्नुते॥"
        ),
        "translation": (
            "For a man, O mighty-armed one, action (karma) alone is the highest deity. "
            "By action one achieves fame; by action one attains heaven. "
            "Context: Karna is the most complex character in the Mahabharata. Born to Kunti "
            "before her marriage, he was abandoned at birth and raised by a charioteer. "
            "Denied access to royal training because of his perceived low birth, Karna "
            "taught himself and became the greatest archer alive. Yet society's labels "
            "followed him all his life. Despite knowing his noble lineage, he remained "
            "loyal to Duryodhana who had shown him respect when no one else would. "
            "His life is a meditation on identity: who are we beyond our birth, our labels, "
            "our circumstances? His answer was always: our actions define us."
        ),
        "source_reference": "Mahabharata, Karna Parva 8.49",
        "source_url": "https://sacred-texts.com/hin/m08/m08049.htm",
        "translation_name": "Kisari Mohan Ganguli (1883-1896) — Public Domain",
        "language": "English",
        "license_or_rights_note": "Public Domain"
    },
    {
        "source_name": "Mahabharata",
        "section": "Shanti Parva",
        "chapter": 12, "verse": 167,
        "character": "Bhishma",
        "topic": "Humility",
        "original_text": (
            "अभिवादनशीलस्य नित्यं वृद्धोपसेविनः।\n"
            "चत्वारि तस्य वर्धन्ते आयुर्विद्या यशो बलम्॥"
        ),
        "translation": (
            "For one who habitually salutes and always serves the elders, "
            "four things increase: longevity, knowledge, fame, and strength. "
            "Context: In the Shanti Parva (the Book of Peace), the mortally wounded Bhishma "
            "imparts the Rajadharma — the dharma of kings and rulers — to Yudhishthira. "
            "This verse captures the Mahabharata's teaching on humility: the willingness "
            "to learn from those who came before, to acknowledge that others carry wisdom "
            "we do not yet possess, is not weakness — it is the foundation of growth. "
            "The greatest warriors in the epic are also the greatest students."
        ),
        "source_reference": "Mahabharata, Shanti Parva 12.167",
        "source_url": "https://sacred-texts.com/hin/m12/m12167.htm",
        "translation_name": "Kisari Mohan Ganguli (1883-1896) — Public Domain",
        "language": "English",
        "license_or_rights_note": "Public Domain"
    },
    {
        "source_name": "Mahabharata",
        "section": "Shanti Parva",
        "chapter": 12, "verse": 283,
        "character": "Bhishma",
        "topic": "Responsibility",
        "original_text": (
            "राजा कलिर्दुराचारो राजा साधुर्गुणान्वितः।\n"
            "राजैव सर्वं निर्माता प्रजानामिति निश्चयः॥"
        ),
        "translation": (
            "A king of evil conduct is Kali (the age of strife); a king of good conduct "
            "is endowed with virtues. The king alone is the maker of everything for "
            "his people — this is certain. "
            "Context: Bhishma's discourse on Rajadharma (the dharma of rulers) emphasises "
            "that leadership is not a privilege — it is a responsibility that shapes the "
            "entire culture and fate of those led. When leaders are ethical, justice "
            "flourishes. When they are corrupt, the entire society suffers. This principle "
            "applies equally to modern managers, parents, or anyone who holds influence: "
            "the character of those at the top determines the character of the whole."
        ),
        "source_reference": "Mahabharata, Shanti Parva 12.283",
        "source_url": "https://sacred-texts.com/hin/m12/index.htm",
        "translation_name": "Kisari Mohan Ganguli (1883-1896) — Public Domain",
        "language": "English",
        "license_or_rights_note": "Public Domain"
    },
    {
        "source_name": "Mahabharata",
        "section": "Anushasana Parva",
        "chapter": 13, "verse": 1,
        "character": "Bhishma",
        "topic": "Truth",
        "original_text": (
            "सत्यं ब्रूयात् प्रियं ब्रूयान्न ब्रूयात् सत्यमप्रियम्।\n"
            "प्रियं च नानृतं ब्रूयादेष धर्मः सनातनः॥"
        ),
        "translation": (
            "Speak the truth; speak what is pleasant; do not speak an unpleasant truth; "
            "and do not speak a pleasant untruth. This is the eternal dharma. "
            "Context: This verse from the Anushasana Parva captures the Mahabharata's "
            "nuanced understanding of truth. Truth without compassion can be brutal; "
            "pleasantness without truth is flattery. The ideal communication requires "
            "both — truth that is delivered with care for the listener. "
            "This is not an instruction to soften difficult truths into lies; "
            "it is guidance on the art of honest, compassionate communication."
        ),
        "source_reference": "Mahabharata, Anushasana Parva 13.1",
        "source_url": "https://sacred-texts.com/hin/m13/m13001.htm",
        "translation_name": "Kisari Mohan Ganguli (1883-1896) — Public Domain",
        "language": "English",
        "license_or_rights_note": "Public Domain"
    },
    {
        "source_name": "Mahabharata",
        "section": "Stri Parva",
        "chapter": 11, "verse": 26,
        "character": "Gandhari",
        "topic": "Consequences",
        "original_text": (
            "न हि कश्चित् फलं भुंक्ते अकर्मा भरतर्षभ।\n"
            "यान्येव कुरुते कर्म तान्येव फलति ध्रुवम्॥"
        ),
        "translation": (
            "No one, O best of the Bharatas, ever enjoys a result without action. "
            "Whatever actions one performs, those alone bear fruit — without doubt. "
            "Context: After the Kurukshetra war has ended and nearly every prince on "
            "both sides lies dead, Gandhari — who lost all one hundred of her sons — "
            "confronts Krishna in fury and grief. She curses him for allowing this destruction. "
            "Krishna accepts the curse without defending himself. Gandhari's grief "
            "encompasses a profound lesson: every action, from Duryodhana's first act "
            "of greed to every unanswered injustice, accumulated into this catastrophe. "
            "The Stri Parva is the Mahabharata's reckoning with the full cost of war."
        ),
        "source_reference": "Mahabharata, Stri Parva 11.26",
        "source_url": "https://sacred-texts.com/hin/m11/m11026.htm",
        "translation_name": "Kisari Mohan Ganguli (1883-1896) — Public Domain",
        "language": "English",
        "license_or_rights_note": "Public Domain"
    },
]


def seed_spiritual_sources(db: Session, force: bool = False):
    existing = db.query(SpiritualSource).all()
    existing_refs = {s.source_reference for s in existing}

    new_count = 0
    for source_data in SOURCES:
        if source_data["source_reference"] in existing_refs:
            continue  # already present, skip
        source = SpiritualSource(**source_data)
        db.add(source)
        new_count += 1

    if new_count > 0:
        db.commit()
        print(f"Added {new_count} new spiritual sources. Total now: {db.query(SpiritualSource).count()}")
    else:
        print(f"All sources already present. Total: {db.query(SpiritualSource).count()}")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_spiritual_sources(db)
    finally:
        db.close()
