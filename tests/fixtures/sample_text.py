"""
Sample text fixtures for testing NLP functionality
"""

SHORT_TEXT = "This is a very short sample text."

MEDIUM_TEXT = """
This is a medium-length sample text for testing purposes.
It contains multiple sentences with varying structures.
Some sentences are short. Others are longer and more complex, with embedded clauses and different punctuation!
The text includes some technical terms like machine learning, artificial intelligence, and data analysis.
"""

LONG_TEXT = """
Natural language processing (NLP) is a subfield of linguistics, computer science, and artificial intelligence concerned with the interactions between computers and human language, in particular how to program computers to process and analyze large amounts of natural language data.

The goal is a computer capable of "understanding" the contents of documents, including the contextual nuances of the language within them. The technology can then accurately extract information and insights contained in the documents as well as categorize and organize the documents themselves.

Challenges in natural language processing frequently involve speech recognition, natural language understanding, and natural language generation. Many different classes of machine-learning algorithms have been applied to natural language-processing tasks. These algorithms take as input a large set of "features" that are generated from the input data.

Some of the earliest-used algorithms, such as decision trees, produced systems of hard if-then rules similar to existing hand-written rules. However, part-of-speech tagging introduced the use of hidden Markov models to NLP, and increasingly, research has focused on statistical models, which make soft, probabilistic decisions based on attaching real-valued weights to each input feature.

The cache language models upon which many speech recognition systems now rely are examples of such statistical models. Such models are generally more robust when given unfamiliar input, especially input that contains errors (as is very common for real-world data), and produce more reliable results when integrated into a larger system comprising multiple subtasks.
"""

EMOTIONAL_TEXT = """
I am absolutely thrilled to announce that we've achieved our biggest milestone yet! This incredible accomplishment wouldn't have been possible without the amazing, dedicated team working tirelessly day and night. I'm so proud of everyone!

The journey hasn't been easy. We've faced numerous heartbreaking setbacks and frustrating obstacles along the way. There were moments of deep disappointment when I feared we wouldn't succeed. The pressure was overwhelming at times.

But now, looking at what we've created, I feel an overwhelming sense of joy and satisfaction. This is truly a dream come true! I can't wait to share our exciting news with the world! The future looks brighter than ever!!!
"""

FORMAL_TEXT = """
The aforementioned findings indicate a statistically significant correlation between the variables in question. It should be noted that these results are consistent with previous research in this domain. Furthermore, the methodology employed herein adheres to established protocols in the field.

The implications of this study extend to various sectors, including but not limited to educational institutions, governmental bodies, and private enterprises. It is imperative that stakeholders consider these findings when formulating future policies.

In conclusion, while this investigation has yielded valuable insights, additional research is warranted to address the limitations inherent in the current study.
"""

INFORMAL_TEXT = """
Hey guys! So I was thinking about that thing we talked about last week, ya know? It's kinda crazy how it all worked out in the end!

Anyway, I gotta tell you about what happened yesterday - it was insane! So there I was, just chillin' at the coffee shop, when this dude comes in and starts singing at the top of his lungs! LOL! Everyone was like "what the heck???" but then we all started clapping... it was awesome!

Btw, did you hear about the new place downtown? We should totally check it out sometime... maybe this weekend? Let me know what you think :)
"""

# Collection of texts with known personality traits for testing
PERSONALITY_SAMPLES = {
    "high_openness": """
        I love exploring new ideas and experiencing different cultures. Yesterday, I spent hours at the modern art museum contemplating the abstract paintings and their meaning. The diversity of human creativity fascinates me. I'm currently reading three different books on philosophy, quantum physics, and ancient mythology - all topics that stretch my thinking in different ways. Next month, I plan to try a completely different cuisine and learn a new language. I believe imagination and curiosity are what make life worth living.
    """,
    "low_openness": """
        I prefer sticking to what I know works. Why change a good routine? I've been eating at the same restaurant every Friday for the past five years - they make the best steak in town, prepared exactly how I like it. I don't understand modern art at all - it just looks like random splotches to me. Classical paintings make sense because you can tell what they're supposed to be. I watch the same TV shows I've always enjoyed and listen to the music I grew up with. New trends come and go, but I know what I like.
    """,
    "high_conscientiousness": """
        I've prepared a detailed five-year plan with specific quarterly goals and monthly checkpoints to ensure I stay on track. My calendar is meticulously organized, with color-coded appointments and buffer time built in between meetings. I never miss deadlines and always arrive 15 minutes early. My workspace is immaculately organized with everything labeled and in its proper place. I maintain detailed records of all projects and review them regularly to identify areas for improvement. Discipline and organization are the foundations of success.
    """,
    "low_conscientiousness": """
        Oops, I completely forgot about our meeting yesterday! I got distracted by a YouTube video and then just decided to grab lunch instead. My apartment is a bit of a mess right now - I keep meaning to clean but never get around to it. I usually start projects with lots of enthusiasm but tend to leave them half-finished when something more interesting comes along. I'm more of a go-with-the-flow person than a planner. Schedules feel too restrictive. I'll probably pay those bills eventually, but they're not urgent yet.
    """,
}
