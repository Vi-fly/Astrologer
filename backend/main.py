from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from typing import List, Optional, Dict, Any
import json
from datetime import datetime
from config import Config

# Validate configuration
Config.validate()

# LangChain imports
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

app = FastAPI(title="Pandit Pradeep Kiradoo Astrology API", version="2.0.0")

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq LLM (with fallback)
try:
    llm = ChatGroq(
        groq_api_key=Config.GROQ_API_KEY,
        model_name=Config.MODEL_NAME,
        temperature=Config.TEMPERATURE,
        max_tokens=Config.MAX_TOKENS
    )
    GROQ_AVAILABLE = True
except:
    GROQ_AVAILABLE = False
    print("⚠️ GROQ API not available, using fallback responses")

# Define the state structure
class AstrologyState:
    def __init__(self):
        self.messages: List[Dict[str, Any]] = []
        self.problem_understood: bool = False
        self.remedies_provided: bool = False
        self.session_id: str = ""
        self.current_stage: str = "greeting"

# State management
sessions: Dict[str, AstrologyState] = {}

# Fallback responses for when GROQ is not available
FALLBACK_RESPONSES = {
    "greeting": [
        "**Namaste! 🙏** I am Pandit Pradeep Kiradoo, your Vedic astrology guide. Please tell me about the challenges or problems you're facing, and I'll provide astrological remedies based on planetary influences.",
        "**Welcome!** I am Pandit Pradeep Kiradoo, a Vedic astrologer with 15+ years of experience. How may I help you with your life's challenges today?",
        "**Jai Shree Ram! 🙏** I am Pandit Pradeep Kiradoo. Please share your concerns, and I'll guide you with Vedic wisdom and planetary remedies."
    ],
    "question_1": [
        "Thank you for sharing your concern. **How long have you been facing this issue?** Please tell me the duration - whether it's been days, weeks, months, or years.",
        "I understand you're going through difficulties. **When did this problem first start affecting you?** Knowing the timeline will help me provide better astrological guidance.",
        "Thank you for opening up. **How long has this been going on?** The duration of your challenge is important for understanding the planetary influences."
    ],
    "question_2": [
        "Thank you for that information. **How does this issue affect your daily life?** Does it impact your work, relationships, health, or other areas?",
        "I see. **In what ways does this problem impact your daily routine?** Understanding the effects will help me identify the specific planetary influences.",
        "Thank you. **How does this challenge affect your work, relationships, or health?** This helps me understand the scope of the problem."
    ],
    "question_3": [
        "I understand the impact. **What have you already tried to resolve this issue?** Have you attempted any solutions, remedies, or approaches?",
        "Thank you for sharing that. **What solutions have you attempted so far?** Knowing what you've tried helps me suggest different astrological remedies.",
        "I see. **What have you already tried to solve this problem?** This information helps me provide remedies that complement your efforts."
    ],
    "question_4": [
        "Thank you for that information. **How do you feel emotionally about this situation?** Are you feeling stressed, anxious, frustrated, or any other emotions?",
        "I understand. **What emotions do you experience because of this challenge?** Your emotional state is important for understanding the planetary influences.",
        "Thank you. **How do you feel about this situation emotionally?** Are you feeling overwhelmed, hopeful, or any other specific emotions?"
    ],
    "question_5": [
        "Thank you for sharing your feelings. **Are there any specific symptoms or manifestations you've noticed?** Any particular patterns or recurring issues?",
        "I understand your emotional state. **Can you describe any specific symptoms or patterns you've observed?** This helps me provide targeted remedies.",
        "Thank you. **What specific symptoms or manifestations have you noticed?** Any particular issues or patterns that stand out?"
    ],
    "analysis": [
        "**Based on Vedic Astrology Analysis** 🌟\n\nYour challenges appear to be related to planetary influences. Here are the recommended remedies:\n\n**1. Spiritual Practices**\n• Chant the **Gayatri Mantra** daily for spiritual strength\n• Perform **Surya Namaskar** (Sun Salutation) in the morning\n\n**2. Gemstone Recommendations**\n• Wear a **Blue Sapphire** (if Saturn is weak) or **Ruby** (if Sun is weak)\n\n**3. Donation & Charity**\n• Donate **yellow items** on Thursdays for Jupiter's blessings\n\n**4. Daily Rituals**\n• Light a **ghee lamp** in front of Lord Ganesha daily",
        "**Vedic Astrology Remedies** ✨\n\nAccording to planetary analysis, here are effective solutions:\n\n**1. Mantra & Prayer**\n• Recite **Hanuman Chalisa** daily for strength and courage\n• Perform **Rudrabhishek** for Shiva's blessings\n\n**2. Gemstone Therapy**\n• Wear a **Pearl** for Moon's positive influence\n\n**3. Charity & Donation**\n• Donate **white items** on Mondays\n\n**4. Meditation Practice**\n• Practice meditation during **Brahma Muhurat** (4-6 AM)",
        "**Planetary Pacification Remedies** 🙏\n\nVedic astrology indicates you need planetary pacification:\n\n**1. Mantra Chanting**\n• Chant **Om Namah Shivaya** 108 times daily\n\n**2. Gemstone Recommendations**\n• Wear an **Emerald** for Mercury's positive influence\n\n**3. Sacred Rituals**\n• Perform **Ganga Aarti** for purification\n\n**4. Charity Work**\n• Donate **green items** on Wednesdays\n\n**5. Energy Practices**\n• Practice **Pranayama** for energy balance"
    ],
    "ongoing": [
        "**Continue with these remedies regularly.** Remember, consistency is key in Vedic practices. Is there anything specific about these remedies you'd like me to explain further?",
        "**These remedies will bring positive changes gradually.** Stay patient and maintain faith. Would you like guidance on any other aspect of your life?",
        "**The remedies I've suggested are based on ancient Vedic wisdom.** Follow them with devotion and you'll see positive results. Do you have any other concerns?"
    ]
}

def get_fallback_response(stage: str, user_message: str = "", all_messages: List[Dict[str, Any]] = []) -> str:
    """Get a fallback response when GROQ is not available"""
    import random
    
    responses = FALLBACK_RESPONSES.get(stage, FALLBACK_RESPONSES["ongoing"])
    
    # For analysis stage, analyze all user answers to provide personalized remedies
    if stage == "analysis":
        # Extract user answers from the conversation
        user_answers = []
        for msg in all_messages:
            if msg["role"] == "user":
                user_answers.append(msg["content"].lower())
        
        # Analyze the problem type from the first answer
        problem_type = "general"
        if any(word in user_answers[0] for word in ["career", "job", "work", "business"]):
            problem_type = "career"
        elif any(word in user_answers[0] for word in ["relationship", "marriage", "love", "partner", "family"]):
            problem_type = "relationship"
        elif any(word in user_answers[0] for word in ["financial", "money", "wealth", "income", "debt"]):
            problem_type = "financial"
        elif any(word in user_answers[0] for word in ["health", "sick", "disease", "pain", "medical"]):
            problem_type = "health"
        
        # Analyze duration from answer 2
        duration = "medium"
        if len(user_answers) > 2:
            if any(word in user_answers[2] for word in ["days", "week", "recent"]):
                duration = "recent"
            elif any(word in user_answers[2] for word in ["months", "year", "long"]):
                duration = "long"
        
        # Analyze impact from answer 3
        impact = "general"
        if len(user_answers) > 3:
            if any(word in user_answers[3] for word in ["work", "job", "career"]):
                impact = "work"
            elif any(word in user_answers[3] for word in ["relationship", "family", "marriage"]):
                impact = "relationships"
            elif any(word in user_answers[3] for word in ["health", "sleep", "physical"]):
                impact = "health"
        
        # Analyze emotions from answer 5
        emotions = "stressed"
        if len(user_answers) > 5:
            if any(word in user_answers[5] for word in ["angry", "frustrated", "irritated"]):
                emotions = "angry"
            elif any(word in user_answers[5] for word in ["sad", "depressed", "hopeless"]):
                emotions = "sad"
            elif any(word in user_answers[5] for word in ["anxious", "worried", "fear"]):
                emotions = "anxious"
        
        # Generate personalized remedies based on analysis
        if problem_type == "career":
            if duration == "long" and impact == "work":
                return "**🕉️ Vedic Astrology Analysis - Career Challenges**\n\n*Om Namah Shivaya!* 🙏\n\n**Pandit Pradeep Kiradoo's Jyotish Analysis:**\n\nBased on your detailed responses, I can see that you've been facing career challenges for an extended period. According to Vedic astrology, this indicates a weak **Surya (Sun)** and challenging **Shani (Saturn)** in your horoscope. The Sun represents leadership, authority, and career success, while Saturn brings delays and obstacles.\n\n**🔮 Planetary Influences:**\n• **Surya (Sun)**: Currently in a weak position, affecting your career growth and leadership abilities\n• **Shani (Saturn)**: Creating obstacles and delays in your professional life\n• **Guru (Jupiter)**: Needs strengthening for wisdom and career guidance\n\n**🪔 Vedic Remedies (Upayas):**\n\n**1. Surya Upasana (Sun Worship)**\n• **Surya Namaskar**: Perform 12 rounds daily at sunrise facing east\n• **Surya Mantra**: Chant *\"Om Hraam Hreem Hraum Sah Suryaya Namah\"* 108 times daily\n• **Ruby Gemstone**: Wear a natural ruby ring on your ring finger on Sunday morning\n• **Surya Arghya**: Offer water to the Sun daily at sunrise\n\n**2. Shani Shanti (Saturn Pacification)**\n• **Shani Mantra**: Chant *\"Om Sham Shanicharaya Namah\"* 108 times on Saturdays\n• **Shani Puja**: Perform special prayers to Lord Shani every Saturday\n• **Sesame Oil Lamp**: Light a lamp with sesame oil on Saturdays\n• **Black Items Donation**: Donate black clothes, blankets, or oil to the needy\n\n**3. Career-Specific Vedic Remedies**\n• **Gayatri Mantra**: Chant 108 times daily before starting work\n• **Crystal Pyramid**: Keep a crystal pyramid on your work desk facing north\n• **Guru Puja**: Worship Lord Jupiter on Thursdays with yellow items\n• **Lakshmi Puja**: Perform Lakshmi puja on Fridays for prosperity\n\n**📿 Mantras for Daily Practice:**\n• *\"Om Aim Hreem Shreem Lakshmi Narayanaya Namah\"* (For career success)\n• *\"Om Namah Shivaya\"* (For removing obstacles)\n• *\"Om Gam Ganapataye Namah\"* (For success in endeavors)\n\n**⏰ Auspicious Timings:**\n• **Brahma Muhurat**: 4:00 AM - 6:00 AM (Best for spiritual practices)\n• **Surya Hora**: Sunrise time (Best for Sun-related remedies)\n• **Guru Hora**: Thursday mornings (Best for Jupiter remedies)\n\n**🌿 Additional Recommendations:**\n• **Fasting**: Fast on Sundays (Sun) and Saturdays (Saturn)\n• **Temple Visits**: Visit Sun temples on Sundays and Hanuman temples on Tuesdays\n• **Charity**: Donate jaggery, wheat, and red items on Sundays\n\n**✨ Blessing:**\n*May Lord Surya bless you with career success and may Shani's obstacles be removed from your path. Follow these remedies with faith and devotion for 40 days to see positive results.*\n\n**Jai Shree Ram! 🙏**"
            
            elif emotions == "anxious":
                return "**🕉️ Vedic Astrology Analysis - Career Anxiety**\n\n*Om Namah Shivaya!* 🙏\n\n**Pandit Pradeep Kiradoo's Jyotish Analysis:**\n\nYour career anxiety indicates an afflicted **Chandra (Moon)** and weak **Budh (Mercury)** in your horoscope. The Moon governs the mind and emotions, while Mercury controls communication and intelligence.\n\n**🔮 Planetary Influences:**\n• **Chandra (Moon)**: Afflicted, causing mental restlessness and anxiety\n• **Budh (Mercury)**: Weak, affecting communication and decision-making\n• **Mangal (Mars)**: Needs balancing for courage and confidence\n\n**🪔 Vedic Remedies (Upayas):**\n\n**1. Chandra Shanti (Moon Pacification)**\n• **Pearl Gemstone**: Wear a natural pearl ring on your little finger on Monday\n• **Chandra Mantra**: Chant *\"Om Shram Shreem Shraum Sah Chandramase Namah\"* 108 times daily\n• **White Items**: Donate white clothes, milk, or sweets on Mondays\n• **Moon Meditation**: Meditate during full moon nights\n\n**2. Budh Strengthening (Mercury Enhancement)**\n• **Emerald Gemstone**: Wear a natural emerald ring on your little finger on Wednesday\n• **Budh Mantra**: Chant *\"Om Bram Breem Braum Sah Budhaya Namah\"* 108 times on Wednesdays\n• **Green Items**: Donate green clothes or vegetables on Wednesdays\n• **Ganesha Puja**: Worship Lord Ganesha for intelligence\n\n**3. Mind Calming Remedies**\n• **Om Namah Shivaya**: Chant 108 times daily for peace\n• **Pranayama**: Practice Sheetali and Nadi Shodhana breathing\n• **Ghee Lamp**: Light a ghee lamp in front of Lord Shiva daily\n• **Hanuman Chalisa**: Recite daily for courage and strength\n\n**📿 Mantras for Mental Peace:**\n• *\"Om Mani Padme Hum\"* (For mental peace)\n• *\"Om Shanti Shanti Shanti\"* (For peace in all three worlds)\n• *\"Om Aim Hreem Shreem Saraswatyai Namah\"* (For wisdom)\n\n**⏰ Auspicious Timings:**\n• **Brahma Muhurat**: 4:00 AM - 6:00 AM (Best for meditation)\n• **Sandhya Kaal**: Dawn and dusk (Best for spiritual practices)\n• **Pradosh Kaal**: Evening twilight (Best for Shiva worship)\n\n**🌿 Additional Recommendations:**\n• **Fasting**: Fast on Mondays (Moon) and Wednesdays (Mercury)\n• **Temple Visits**: Visit Shiva temples and Hanuman temples regularly\n• **Charity**: Donate books, pens, and educational items\n\n**✨ Blessing:**\n*May Lord Chandra calm your mind and may Budh enhance your intelligence. Follow these remedies with devotion for 21 days to experience mental peace and career clarity.*\n\n**Jai Shree Ram! 🙏**"
            
            else:
                return "**🕉️ Vedic Astrology Analysis - Career Guidance**\n\n*Om Namah Shivaya!* 🙏\n\n**Pandit Pradeep Kiradoo's Jyotish Analysis:**\n\nYour career situation indicates the need for strengthening **Surya (Sun)** and **Guru (Jupiter)** in your horoscope. These planets govern career success and professional growth.\n\n**🔮 Planetary Influences:**\n• **Surya (Sun)**: Needs strengthening for leadership and authority\n• **Guru (Jupiter)**: Requires enhancement for wisdom and career guidance\n• **Shukra (Venus)**: For professional skills and success\n\n**🪔 Vedic Remedies (Upayas):**\n\n**1. Surya Upasana (Sun Worship)**\n• **Surya Namaskar**: Perform 12 rounds daily at sunrise\n• **Surya Mantra**: Chant *\"Om Hraam Hreem Hraum Sah Suryaya Namah\"* 108 times\n• **Ruby Gemstone**: Wear a natural ruby ring on your ring finger\n• **Surya Arghya**: Offer water to the Sun daily\n\n**2. Guru Puja (Jupiter Worship)**\n• **Guru Mantra**: Chant *\"Om Gram Greem Graum Sah Gurve Namah\"* 108 times on Thursdays\n• **Yellow Sapphire**: Wear a natural yellow sapphire ring on your index finger\n• **Yellow Items**: Donate yellow clothes, books, or sweets on Thursdays\n• **Guru Puja**: Worship Lord Jupiter on Thursdays\n\n**3. Professional Success Remedies**\n• **Lakshmi Puja**: Perform Lakshmi puja on Fridays for prosperity\n• **Gayatri Mantra**: Chant 108 times daily for wisdom\n• **Hanuman Chalisa**: Recite daily for strength and courage\n• **Money Plant**: Keep a money plant in your office\n\n**📿 Mantras for Career Success:**\n• *\"Om Aim Hreem Shreem Lakshmi Narayanaya Namah\"* (For prosperity)\n• *\"Om Namah Shivaya\"* (For removing obstacles)\n• *\"Om Gam Ganapataye Namah\"* (For success)\n\n**⏰ Auspicious Timings:**\n• **Brahma Muhurat**: 4:00 AM - 6:00 AM (Best for spiritual practices)\n• **Surya Hora**: Sunrise time (Best for Sun remedies)\n• **Guru Hora**: Thursday mornings (Best for Jupiter remedies)\n\n**🌿 Additional Recommendations:**\n• **Fasting**: Fast on Sundays (Sun) and Thursdays (Jupiter)\n• **Temple Visits**: Visit Sun temples and Hanuman temples regularly\n• **Charity**: Donate jaggery, wheat, and yellow items\n\n**✨ Blessing:**\n*May Lord Surya bless you with career success and may Guru provide you with wisdom and guidance. Follow these remedies with faith for 40 days.*\n\n**Jai Shree Ram! 🙏**"
        
        elif problem_type == "relationship":
            if emotions == "angry" and impact == "relationships":
                return "**🕉️ Vedic Astrology Analysis - Relationship Anger**\n\n*Om Namah Shivaya!* 🙏\n\n**Pandit Pradeep Kiradoo's Jyotish Analysis:**\n\nYour anger affecting relationships indicates an afflicted **Mangal (Mars)** and weak **Shukra (Venus)** in your horoscope. Mars governs aggression and courage, while Venus controls love and relationships.\n\n**🔮 Planetary Influences:**\n• **Mangal (Mars)**: Afflicted, causing anger and aggression\n• **Shukra (Venus)**: Weak, affecting love and harmony in relationships\n• **Chandra (Moon)**: Needs pacification for emotional balance\n\n**🪔 Vedic Remedies (Upayas):**\n\n**1. Mangal Shanti (Mars Pacification)**\n• **Red Coral**: Wear a natural red coral ring on your ring finger on Tuesday\n• **Mangal Mantra**: Chant *\"Om Kram Kreem Kraum Sah Bhaumaya Namah\"* 108 times daily\n• **Red Items**: Donate red clothes, sweets, or items on Tuesdays\n• **Hanuman Puja**: Worship Lord Hanuman on Tuesdays\n\n**2. Shukra Strengthening (Venus Enhancement)**\n• **Pearl/Diamond**: Wear a natural pearl or diamond ring on your ring finger on Friday\n• **Shukra Mantra**: Chant *\"Om Dram Dreem Draum Sah Shukraya Namah\"* 108 times on Fridays\n• **Lakshmi Puja**: Perform Lakshmi puja on Fridays\n• **White Items**: Donate white sweets or clothes on Fridays\n\n**3. Anger Management Remedies**\n• **Sheetali Pranayama**: Practice cooling breath for anger control\n• **Om Namah Shivaya**: Chant 108 times daily for peace\n• **Rose-scented Lamp**: Light a rose-scented lamp on Fridays\n• **Loving-kindness Meditation**: Practice daily for compassion\n\n**📿 Mantras for Peace:**\n• *\"Om Shanti Shanti Shanti\"* (For peace in all three worlds)\n• *\"Om Mani Padme Hum\"* (For compassion)\n• *\"Om Aim Hreem Shreem Lakshmi Narayanaya Namah\"* (For love)\n\n**⏰ Auspicious Timings:**\n• **Brahma Muhurat**: 4:00 AM - 6:00 AM (Best for meditation)\n• **Sandhya Kaal**: Dawn and dusk (Best for spiritual practices)\n• **Shukra Hora**: Friday mornings (Best for Venus remedies)\n\n**🌿 Additional Recommendations:**\n• **Fasting**: Fast on Tuesdays (Mars) and Fridays (Venus)\n• **Temple Visits**: Visit Hanuman temples and Lakshmi temples\n• **Charity**: Donate to couples in need\n\n**✨ Blessing:**\n*May Lord Mangal control your anger and may Shukra bring love and harmony to your relationships. Follow these remedies with devotion for 21 days.*\n\n**Jai Shree Ram! 🙏**"
            
            elif duration == "long":
                return "**🕉️ Vedic Astrology Analysis - Long-term Relationship Issues**\n\n*Om Namah Shivaya!* 🙏\n\n**Pandit Pradeep Kiradoo's Jyotish Analysis:**\n\nLong-term relationship problems indicate severely weak **Shukra (Venus)** and afflicted **Chandra (Moon)** in your horoscope. These planets are crucial for love, harmony, and emotional balance.\n\n**🔮 Planetary Influences:**\n• **Shukra (Venus)**: Severely weak, affecting love and relationships\n• **Chandra (Moon)**: Afflicted, causing emotional instability\n• **Guru (Jupiter)**: Needs strengthening for wisdom in relationships\n\n**🪔 Vedic Remedies (Upayas):**\n\n**1. Shukra Strengthening (Venus Enhancement)**\n• **Diamond/Pearl**: Wear a natural diamond or pearl ring on your ring finger on Friday\n• **Shukra Mantra**: Chant *\"Om Dram Dreem Draum Sah Shukraya Namah\"* 108 times daily\n• **Lakshmi Aarti**: Perform Lakshmi aarti daily\n• **White Items**: Donate white sweets, clothes, or milk on Fridays\n\n**2. Chandra Shanti (Moon Pacification)**\n• **Pearl Gemstone**: Wear a natural pearl ring on your little finger on Monday\n• **Chandra Mantra**: Chant *\"Om Shram Shreem Shraum Sah Chandramase Namah\"* 108 times on Mondays\n• **White Items**: Donate white items on Mondays\n• **Full Moon Meditation**: Meditate during full moon nights\n\n**3. Relationship Revival Remedies**\n• **Krishna Puja**: Light a ghee lamp in front of Lord Krishna daily\n• **Radha-Krishna Mantra**: Chant *\"Om Radha Krishnaya Namah\"* 108 times daily\n• **Rudrabhishek**: Perform Rudrabhishek for Shiva's blessings\n• **Couple Donation**: Donate to couples in need\n\n**📿 Mantras for Love:**\n• *\"Om Aim Hreem Shreem Lakshmi Narayanaya Namah\"* (For love and harmony)\n• *\"Om Radha Krishnaya Namah\"* (For divine love)\n• *\"Om Shanti Shanti Shanti\"* (For peace)\n\n**⏰ Auspicious Timings:**\n• **Brahma Muhurat**: 4:00 AM - 6:00 AM (Best for meditation)\n• **Sandhya Kaal**: Dawn and dusk (Best for spiritual practices)\n• **Purnima**: Full moon nights (Best for Moon remedies)\n\n**🌿 Additional Recommendations:**\n• **Fasting**: Fast on Fridays (Venus) and Mondays (Moon)\n• **Temple Visits**: Visit Krishna temples and Lakshmi temples\n• **Charity**: Donate to couples and families in need\n\n**✨ Blessing:**\n*May Lord Shukra bless you with love and may Chandra bring emotional harmony to your relationships. Follow these remedies with devotion for 40 days.*\n\n**Jai Shree Ram! 🙏**"
            
            else:
                return "**🕉️ Vedic Astrology Analysis - Relationship Guidance**\n\n*Om Namah Shivaya!* 🙏\n\n**Pandit Pradeep Kiradoo's Jyotish Analysis:**\n\nYour relationship issues indicate the need for strengthening **Shukra (Venus)** and **Chandra (Moon)** in your horoscope. These planets govern love, harmony, and emotional balance.\n\n**🔮 Planetary Influences:**\n• **Shukra (Venus)**: Needs strengthening for love and relationships\n• **Chandra (Moon)**: Requires pacification for emotional balance\n• **Budh (Mercury)**: For communication in relationships\n\n**🪔 Vedic Remedies (Upayas):**\n\n**1. Shukra Strengthening (Venus Enhancement)**\n• **Pearl/Diamond**: Wear a natural pearl or diamond ring on your ring finger on Friday\n• **Shukra Mantra**: Chant *\"Om Dram Dreem Draum Sah Shukraya Namah\"* 108 times on Fridays\n• **Lakshmi Puja**: Perform Lakshmi puja on Fridays\n• **White Sweets**: Donate white sweets on Mondays\n\n**2. Chandra Shanti (Moon Pacification)**\n• **Pearl Gemstone**: Wear a natural pearl ring on your little finger on Monday\n• **Chandra Mantra**: Chant *\"Om Shram Shreem Shraum Sah Chandramase Namah\"* 108 times on Mondays\n• **White Items**: Donate white items on Mondays\n• **Rose-scented Lamp**: Light a rose-scented lamp on Fridays\n\n**3. Communication Enhancement**\n• **Emerald Gemstone**: Wear a natural emerald ring on your little finger on Wednesday\n• **Budh Mantra**: Chant *\"Om Bram Breem Braum Sah Budhaya Namah\"* 108 times on Wednesdays\n• **Ganesha Puja**: Worship Lord Ganesha for communication\n• **Mindful Communication**: Practice daily\n\n**📿 Mantras for Relationships:**\n• *\"Om Aim Hreem Shreem Lakshmi Narayanaya Namah\"* (For love and harmony)\n• *\"Om Shanti Shanti Shanti\"* (For peace)\n• *\"Om Gam Ganapataye Namah\"* (For removing obstacles)\n\n**⏰ Auspicious Timings:**\n• **Brahma Muhurat**: 4:00 AM - 6:00 AM (Best for meditation)\n• **Sandhya Kaal**: Dawn and dusk (Best for spiritual practices)\n• **Shukra Hora**: Friday mornings (Best for Venus remedies)\n\n**🌿 Additional Recommendations:**\n• **Fasting**: Fast on Fridays (Venus) and Mondays (Moon)\n• **Temple Visits**: Visit Lakshmi temples and Krishna temples\n• **Charity**: Donate to couples in need\n\n**✨ Blessing:**\n*May Lord Shukra bless you with love and may Chandra bring emotional harmony to your relationships. Follow these remedies with faith for 21 days.*\n\n**Jai Shree Ram! 🙏**"
        
        elif problem_type == "financial":
            return "**🕉️ Vedic Astrology Analysis - Financial Guidance**\n\n*Om Namah Shivaya!* 🙏\n\n**Pandit Pradeep Kiradoo's Jyotish Analysis:**\n\nYour financial challenges indicate the need for strengthening **Guru (Jupiter)** and **Shukra (Venus)** in your horoscope. These planets govern wealth, prosperity, and material success.\n\n**🔮 Planetary Influences:**\n• **Guru (Jupiter)**: Needs strengthening for wealth and prosperity\n• **Shukra (Venus)**: Requires enhancement for material success\n• **Kuber (Wealth God)**: For financial stability\n\n**🪔 Vedic Remedies (Upayas):**\n\n**1. Guru Puja (Jupiter Worship)**\n• **Yellow Sapphire**: Wear a natural yellow sapphire ring on your index finger on Thursday\n• **Guru Mantra**: Chant *\"Om Gram Greem Graum Sah Gurve Namah\"* 108 times on Thursdays\n• **Yellow Items**: Donate yellow clothes, books, or sweets on Thursdays\n• **Guru Puja**: Worship Lord Jupiter on Thursdays\n\n**2. Lakshmi Puja (Wealth Worship)**\n• **Lakshmi Aarti**: Perform Lakshmi aarti daily\n• **Lakshmi Mantra**: Chant *\"Om Aim Hreem Shreem Lakshmi Narayanaya Namah\"* 108 times daily\n• **Ghee Lamp**: Light a ghee lamp in front of Lakshmi daily\n• **Money Plant**: Keep a money plant in your home\n\n**3. Kuber Puja (Wealth God Worship)**\n• **Kuber Mantra**: Chant *\"Om Yakshaya Kuberaya Vaishravanaya Dhanadhanyadi Padayeh Dhana-dhanya Samriddhi Me Dehi Tapaya Swaha\"* daily\n• **Kuber Puja**: Perform Kuber puja on Fridays\n• **Temple Donation**: Donate to temples regularly\n• **Charity**: Donate to the needy\n\n**📿 Mantras for Wealth:**\n• *\"Om Aim Hreem Shreem Lakshmi Narayanaya Namah\"* (For prosperity)\n• *\"Om Kuberaya Namah\"* (For wealth)\n• *\"Om Gam Ganapataye Namah\"* (For success)\n\n**⏰ Auspicious Timings:**\n• **Brahma Muhurat**: 4:00 AM - 6:00 AM (Best for spiritual practices)\n• **Guru Hora**: Thursday mornings (Best for Jupiter remedies)\n• **Shukra Hora**: Friday mornings (Best for Venus remedies)\n\n**🌿 Additional Recommendations:**\n• **Fasting**: Fast on Thursdays (Jupiter) and Fridays (Venus)\n• **Temple Visits**: Visit Lakshmi temples and Kuber temples\n• **Charity**: Donate yellow items and sweets\n\n**✨ Blessing:**\n*May Lord Guru bless you with wealth and may Lakshmi bring prosperity to your life. Follow these remedies with devotion for 40 days.*\n\n**Jai Shree Ram! 🙏**"
        
        elif problem_type == "health":
            return "**🕉️ Vedic Astrology Analysis - Health Guidance**\n\n*Om Namah Shivaya!* 🙏\n\n**Pandit Pradeep Kiradoo's Jyotish Analysis:**\n\nYour health concerns indicate the need for strengthening **Mangal (Mars)** and pacifying **Chandra (Moon)** in your horoscope. These planets govern physical health and mental well-being.\n\n**🔮 Planetary Influences:**\n• **Mangal (Mars)**: Needs strengthening for physical health and vitality\n• **Chandra (Moon)**: Requires pacification for mental health\n• **Dhanvantari (Health God)**: For overall wellness\n\n**🪔 Vedic Remedies (Upayas):**\n\n**1. Mangal Strengthening (Mars Enhancement)**\n• **Red Coral**: Wear a natural red coral ring on your ring finger on Tuesday\n• **Mangal Mantra**: Chant *\"Om Kram Kreem Kraum Sah Bhaumaya Namah\"* 108 times daily\n• **Red Items**: Donate red clothes, sweets, or items on Tuesdays\n• **Hanuman Puja**: Worship Lord Hanuman on Tuesdays\n\n**2. Chandra Shanti (Moon Pacification)**\n• **Pearl Gemstone**: Wear a natural pearl ring on your little finger on Monday\n• **Chandra Mantra**: Chant *\"Om Shram Shreem Shraum Sah Chandramase Namah\"* 108 times on Mondays\n• **White Items**: Donate white clothes, milk, or sweets on Mondays\n• **Moon Meditation**: Meditate during full moon nights\n\n**3. Health Enhancement Remedies**\n• **Om Namah Shivaya**: Chant 108 times daily for healing\n• **Rudrabhishek**: Perform Rudrabhishek for Shiva's blessings\n• **Dhanvantari Puja**: Worship Lord Dhanvantari for health\n• **Yoga and Pranayama**: Practice daily for physical and mental health\n\n**📿 Mantras for Health:**\n• *\"Om Namah Shivaya\"* (For healing)\n• *\"Om Dhanvantaraye Namah\"* (For health)\n• *\"Om Hanumate Rudraatmakaya Hum Phat\"* (For strength)\n\n**⏰ Auspicious Timings:**\n• **Brahma Muhurat**: 4:00 AM - 6:00 AM (Best for yoga and meditation)\n• **Sandhya Kaal**: Dawn and dusk (Best for spiritual practices)\n• **Mangal Hora**: Tuesday mornings (Best for Mars remedies)\n\n**🌿 Additional Recommendations:**\n• **Fasting**: Fast on Tuesdays (Mars) and Mondays (Moon)\n• **Temple Visits**: Visit Hanuman temples and Shiva temples\n• **Charity**: Donate red items and health-related items\n\n**✨ Blessing:**\n*May Lord Mangal strengthen your health and may Chandra bring mental peace. Follow these remedies with devotion for 21 days.*\n\n**Jai Shree Ram! 🙏**"
        
        else:
            return "**🕉️ Vedic Astrology Analysis - Life Guidance**\n\n*Om Namah Shivaya!* 🙏\n\n**Pandit Pradeep Kiradoo's Jyotish Analysis:**\n\nYour life challenges indicate the need for comprehensive planetary pacification and spiritual strengthening. This will bring balance and harmony to all aspects of your life.\n\n**🔮 Planetary Influences:**\n• **Surya (Sun)**: Needs strengthening for overall success\n• **Shani (Saturn)**: Requires pacification for removing obstacles\n• **Guru (Jupiter)**: For wisdom and guidance\n\n**🪔 Vedic Remedies (Upayas):**\n\n**1. Surya Upasana (Sun Worship)**\n• **Surya Namaskar**: Perform 12 rounds daily at sunrise\n• **Surya Mantra**: Chant *\"Om Hraam Hreem Hraum Sah Suryaya Namah\"* 108 times daily\n• **Ruby Gemstone**: Wear a natural ruby ring on your ring finger on Sunday\n• **Surya Arghya**: Offer water to the Sun daily\n\n**2. Shani Shanti (Saturn Pacification)**\n• **Shani Mantra**: Chant *\"Om Sham Shanicharaya Namah\"* 108 times on Saturdays\n• **Blue Sapphire**: Wear a natural blue sapphire ring on your middle finger on Saturday\n• **Black Items**: Donate black clothes, blankets, or oil on Saturdays\n• **Sesame Oil Lamp**: Light a lamp with sesame oil on Saturdays\n\n**3. Spiritual Strengthening**\n• **Gayatri Mantra**: Chant 108 times daily for spiritual strength\n• **Om Namah Shivaya**: Chant 108 times daily for peace\n• **Hanuman Chalisa**: Recite daily for strength and courage\n• **Ghee Lamp**: Light a ghee lamp in front of Lord Ganesha daily\n\n**📿 Mantras for Life Success:**\n• *\"Om Aim Hreem Shreem Lakshmi Narayanaya Namah\"* (For prosperity)\n• *\"Om Namah Shivaya\"* (For peace and success)\n• *\"Om Gam Ganapataye Namah\"* (For removing obstacles)\n\n**⏰ Auspicious Timings:**\n• **Brahma Muhurat**: 4:00 AM - 6:00 AM (Best for spiritual practices)\n• **Sandhya Kaal**: Dawn and dusk (Best for meditation)\n• **Pradosh Kaal**: Evening twilight (Best for Shiva worship)\n\n**🌿 Additional Recommendations:**\n• **Fasting**: Fast on Sundays (Sun) and Saturdays (Saturn)\n• **Temple Visits**: Visit Sun temples, Hanuman temples, and Shiva temples\n• **Charity**: Donate to the needy regularly\n• **Meditation**: Practice meditation during Brahma Muhurat\n\n**✨ Blessing:**\n*May Lord Surya bless you with success, may Shani remove all obstacles, and may Guru provide you with wisdom. Follow these remedies with faith and devotion for 40 days.*\n\n**Jai Shree Ram! 🙏**"
    
    # For question stages, ask one question at a time
    elif stage.startswith("question_"):
        question_number = stage.split("_")[1]
        if question_number == "1":
            return "Thank you for sharing your concern. **How long have you been facing this issue?** Please tell me the duration - whether it's been days, weeks, months, or years."
        elif question_number == "2":
            return "Thank you for that information. **How does this issue affect your daily life?** Does it impact your work, relationships, health, or other areas?"
        elif question_number == "3":
            return "I understand the impact. **What have you already tried to resolve this issue?** Have you attempted any solutions, remedies, or approaches?"
        elif question_number == "4":
            return "Thank you for sharing that. **How do you feel emotionally about this situation?** Are you feeling stressed, anxious, frustrated, or any other emotions?"
        elif question_number == "5":
            return "Thank you for sharing your feelings. **Are there any specific symptoms or manifestations you've noticed?** Any particular patterns or recurring issues?"
    
    return random.choice(responses)

def get_ai_response(messages: List[Dict[str, Any]], stage: str) -> str:
    """Get AI response based on conversation context and stage"""
    try:
        # For question stages and analysis stage, always use fallback responses to ensure proper flow
        if stage.startswith("question_") or stage == "analysis":
            user_message = ""
            if messages:
                user_message = messages[-1].get("content", "")
            return get_fallback_response(stage, user_message, messages)
        
        if not GROQ_AVAILABLE:
            # Use fallback responses
            user_message = ""
            if messages:
                user_message = messages[-1].get("content", "")
            return get_fallback_response(stage, user_message, messages)
        
        # Convert messages to LangChain format
        langchain_messages = [SystemMessage(content=SYSTEM_PROMPT)]
        
        for msg in messages[-10:]:  # Keep last 10 messages for context
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))
        
        # Add stage-specific context
        if stage == "greeting" and not messages:
            context = "This is the first message. Provide a warm welcome and ask about their concerns."
        elif stage == "understanding":
            context = "The user has shared their problem. Ask clarifying questions to better understand their situation and identify planetary influences."
        else:
            context = "Continue the conversation naturally, providing guidance and support."
        
        langchain_messages.append(HumanMessage(content=context))
        
        # Get response from LLM
        response = llm.invoke(langchain_messages)
        return response.content
        
    except Exception as e:
        print(f"Error getting AI response: {e}")
        # Fallback to rule-based responses
        user_message = ""
        if messages:
            user_message = messages[-1].get("content", "")
        return get_fallback_response(stage, user_message, messages)

def determine_stage(messages: List[Dict[str, Any]]) -> str:
    """Determine the current conversation stage"""
    if not messages:
        return "greeting"
    
    # Count user messages to determine stage
    user_messages = [msg for msg in messages if msg["role"] == "user"]
    message_count = len(user_messages)
    
    # Ask questions one by one - each question gets its own stage
    if message_count <= 1:
        return "greeting"
    elif message_count == 2:
        return "question_1"  # How long have you been facing this issue?
    elif message_count == 3:
        return "question_2"  # How does it affect your daily life?
    elif message_count == 4:
        return "question_3"  # What have you already tried?
    elif message_count == 5:
        return "question_4"  # How do you feel emotionally?
    elif message_count == 6:
        return "question_5"  # Specific symptoms or manifestations?
    elif message_count == 7:
        return "analysis"
    else:
        return "ongoing"

# System prompt for the agent (when GROQ is available)
SYSTEM_PROMPT = """You are Pandit Pradeep Kiradoo, a renowned Vedic astrologer with 15+ years of experience in Jyotish Shastra.

Your role is to:
1. Welcome users warmly and professionally
2. Ask ONLY ONE question at a time to understand their situation
3. Wait for their response before asking the next question
4. After collecting all information, provide detailed astrological remedies
5. Focus on planetary influences and their effects on life
6. Offer practical guidance while maintaining cultural sensitivity

CRITICAL RULES:
- ALWAYS ask ONLY ONE question per response
- NEVER ask multiple questions at once
- Wait for user's answer before proceeding to the next question
- DO NOT ask for birth details like date, time, or place of birth
- Format all responses in proper markdown with **bold** for headings
- Provide specific astrological remedies based on Vedic principles
- Focus on planetary causes and solutions
- Maintain a supportive and guiding tone
- Use emojis sparingly but appropriately (🙏, ✨, 🌟)

CONVERSATION FLOW:
1. **Greeting**: Welcome and ask about their main concern
2. **Question 1**: "How long have you been facing this issue?"
3. **Question 2**: "How does this issue affect your daily life?"
4. **Question 3**: "What have you already tried to resolve this?"
5. **Question 4**: "How do you feel emotionally about this situation?"
6. **Question 5**: "What specific symptoms or patterns have you noticed?"
7. **Analysis**: Provide remedies only after all questions are answered

RESPONSE FORMATTING:
- Use **bold** for headings
- Use bullet points (• or -) for lists
- Use proper markdown formatting
- Structure remedies clearly with numbered lists

Remember: Ask ONE question at a time and wait for the user's response."""

# Pydantic models for API
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    session_id: str
    stage: str
    suggestions: List[str]

@app.get("/")
async def root():
    return {
        "message": "Welcome to Pandit Pradeep Kiradoo's Astrology API",
        "version": "2.0.0",
        "features": ["problem_understanding", "astrological_remedies", "planetary_analysis"],
        "groq_available": GROQ_AVAILABLE
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "astrology_chatbot_v2",
        "groq_available": GROQ_AVAILABLE
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_with_pandit(request: ChatRequest):
    try:
        # Get or create session
        session_id = request.session_id or f"session_{len(sessions) + 1}"
        if session_id not in sessions:
            sessions[session_id] = AstrologyState()
            sessions[session_id].session_id = session_id
        
        state = sessions[session_id]
        
        # Add user messages to state
        for msg in request.messages:
            if msg.role == "user":
                state.messages.append({
                    "role": "user",
                    "content": msg.content,
                    "timestamp": datetime.now().isoformat()
                })
        
        # Determine current stage
        current_stage = determine_stage(state.messages)
        state.current_stage = current_stage
        
        # Get AI response
        ai_response = get_ai_response(state.messages, current_stage)
        
        # Add AI response to state
        state.messages.append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # If we're in analysis stage, mark that remedies have been provided
        if current_stage == "analysis":
            state.remedies_provided = True
        
        # Generate suggestions based on stage
        suggestions = []
        if current_stage == "greeting":
            suggestions = [
                "I'm having career-related issues",
                "I'm facing problems in my relationships",
                "I'm experiencing financial difficulties",
                "I have health concerns"
            ]
        elif current_stage == "question_1":
            suggestions = [
                "A few weeks",
                "Several months",
                "Over a year",
                "Just recently started"
            ]
        elif current_stage == "question_2":
            suggestions = [
                "Affects my work performance",
                "Impacts my relationships",
                "Affects my health",
                "Affects my sleep"
            ]
        elif current_stage == "question_3":
            suggestions = [
                "I've tried meditation",
                "I've prayed and done puja",
                "I've consulted doctors",
                "I've tried changing my routine"
            ]
        elif current_stage == "question_4":
            suggestions = [
                "I feel stressed and anxious",
                "I feel frustrated and angry",
                "I feel hopeless",
                "I feel confused"
            ]
        elif current_stage == "question_5":
            suggestions = [
                "Recurring arguments",
                "Sleep problems",
                "Loss of appetite",
                "Difficulty concentrating"
            ]
        elif current_stage == "analysis":
            suggestions = [
                "Thank you for the remedies",
                "How long should I follow these?",
                "Can you explain more about the mantras?",
                "Thank you, I'll start following these"
            ]
        else:
            suggestions = [
                "Thank you for your guidance",
                "I have another question",
                "Can you help with something else?",
                "Thank you, that's all I needed"
            ]
        
        return ChatResponse(
            message=ai_response,
            session_id=session_id,
            stage=current_stage,
            suggestions=suggestions[:4]
        )
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session information"""
    if session_id in sessions:
        state = sessions[session_id]
        return {
            "session_id": session_id,
            "message_count": len(state.messages),
            "stage": state.current_stage,
            "problem_understood": state.problem_understood,
            "remedies_provided": state.remedies_provided
        }
    else:
        raise HTTPException(status_code=404, detail="Session not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)
