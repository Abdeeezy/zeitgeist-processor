import anthropic
import json
import time

from dotenv import load_dotenv, dotenv_values


load_dotenv()  # Load environment variables into the environment
dictValues = dotenv_values(".env")  # Load environment variables from .env file


client = anthropic.Anthropic(api_key=dictValues['ANTHROPIC_API_KEY'])

def score_article_themes(keywords: list[str], headline: str) -> dict:

    # Default neutral scores for all leaf nodes
    default_scores = {
        "Renewal": 0.1, "Aspiration": 0.1, "Resilience": 0.1,
        "Compassion": 0.1, "Unity": 0.1, "Devotion": 0.1,
        "Abundance": 0.1, "Sacrifice": 0.1, "Sharing": 0.1,
        "Equilibrium": 0.1, "Moderation": 0.1, "Cyclical": 0.1,
        "Transformation": 0.1, "Adaptation": 0.1, "Flow": 0.1,
        "Unknown": 0.1, "Potential": 0.1, "Ambiguity": 0.1,
        "Entropy": 0.1, "Corruption": 0.1, "Erosion": 0.1,
        "Control": 0.1, "Subjugation": 0.1, "Tyranny": 0.1,
        "Separation": 0.1, "Void": 0.1, "Desolation": 0.1
    }

    try:
        prompt = f"""Score this article's alignment with these thematic concepts (0.0 to 1.0):

                Article headline: {headline}
                Keywords: {', '.join(keywords)}

                Themes to score:
                - Renewal
                - Aspiration
                - Resilience
                - Compassion
                - Unity
                - Devotion
                - Abundance
                - Sacrifice
                - Sharing
                - Equilibrium
                - Moderation
                - Cyclical
                - Transformation
                - Adaptation
                - Flow
                - Unknown
                - Potentia
                - Ambiguity
                - Entropy
                - Corruption
                - Erosion
                - Control
                - Subjugation
                - Tyranny
                - Separation
                - Void 
                - Desolation

                Return ONLY a JSON object with scores for each theme."""

        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        print("raw response text: \n\n" + response.content[0].text)


        # Parse JSON from response
        text = response.content[0].text.strip()
        text = text.removeprefix('```json').removesuffix('```').strip()

        # json object turns into a dictionary, {"Renewal": 0.8, "Aspiration": 0.4, ...}
        return json.loads(text)
    
    except Exception as e:
        print(f"⚠️ Failed to score article '{headline[:50]}...': {e}")
        print(f"   Using default neutral scores")
        return default_scores
    


def score_articles_batch(articles_data: list[dict], batch_size: int = 5) -> list[dict]:

    """
    Score multiple articles in batches, respecting rate limits.
    
    Args:
        articles_data: List of dicts with 'keywords' and 'headline' keys
        batch_size: Number of articles to score per API call (default 5)
    
    Returns:
        List of score dictionaries, one per article
    """

    all_scores = []

    
    for i in range(0, len(articles_data), batch_size):
        batch = articles_data[i:i+batch_size]

        try:

            # Build prompt with multiple articles
            articles_text = ""
            for idx, article in enumerate(batch):
                articles_text += f"\nArticle {idx + 1}:\n"
                articles_text += f"Headline: {article['headline']}\n"
                articles_text += f"Keywords: {', '.join(article['keywords'])}\n"
            

            prompt = f"""Score this article's alignment with these thematic concepts (0.0 to 1.0):

                    {articles_text}

                    Themes to score:
                    - Renewal
                    - Aspiration
                    - Resilience
                    - Compassion
                    - Unity
                    - Devotion
                    - Abundance
                    - Sacrifice
                    - Sharing
                    - Equilibrium
                    - Moderation
                    - Cyclical
                    - Transformation
                    - Adaptation
                    - Flow
                    - Unknown
                    - Potentia
                    - Ambiguity
                    - Entropy
                    - Corruption
                    - Erosion
                    - Control
                    - Subjugation
                    - Tyranny
                    - Separation
                    - Void 
                    - Desolation

                    Return ONLY a JSON array where each element is the scores for one article, in order.
                    Example: [{{"Renewal": 0.5, "Aspiration": 0.3, ...}}, {{"Renewal": 0.8, ...}}, ...]
                    """       

            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            print("raw response text: \n\n" + response.content[0].text)


            # Parse JSON from response
            text = response.content[0].text.strip()
            text = text.removeprefix('```json').removesuffix('```').strip()

            batch_scores = json.loads(text)
            all_scores.extend(batch_scores)
            
            print(f"✅ Scored articles {i+1}-{min(i+batch_size, len(articles_data))}")
            
        except Exception as e:
            print(f"⚠️ Failed to score article {i//batch_size + 1}: {e}")
            print(f"   Using default neutral scores for this batch")

            # Default neutral scores for all leaf nodes
            default_scores = {
                "Renewal": 0.1, "Aspiration": 0.1, "Resilience": 0.1,
                "Compassion": 0.1, "Unity": 0.1, "Devotion": 0.1,
                "Abundance": 0.1, "Sacrifice": 0.1, "Sharing": 0.1,
                "Equilibrium": 0.1, "Moderation": 0.1, "Cyclical": 0.1,
                "Transformation": 0.1, "Adaptation": 0.1, "Flow": 0.1,
                "Unknown": 0.1, "Potential": 0.1, "Ambiguity": 0.1,
                "Entropy": 0.1, "Corruption": 0.1, "Erosion": 0.1,
                "Control": 0.1, "Subjugation": 0.1, "Tyranny": 0.1,
                "Separation": 0.1, "Void": 0.1, "Desolation": 0.1
            }
            all_scores.extend([default_scores] * len(batch))
    
        # Rate limit: wait 60 seconds between batches
        if i + batch_size < len(articles_data):
            print(f"⏳ Waiting 60s for rate limit...")
            time.sleep(60)

        return all_scores