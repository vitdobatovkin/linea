import asyncio
import random
import aiohttp

async def generate_random_dapp_review(dex_name):
    templates = [
        # Full-length templates
        "Discovering {dex} was a game-changer for how I {verb} my {noun}",
        "{dex} has revolutionized my approach to {noun} {verb}",
        "In the world of {noun}, {dex} stands out as a {adjective} option",
        "Glad I switched to {dex} for all my {noun} {verb} needs",
        "Efficiency and ease are what make {dex} my favorite for {verb} {noun}",
        "The {adjective} service {dex} offers for {noun} {verb} is unmatched",
        "{dex} has made {verb} {noun} {adverb} straightforward",
        "I’m {adverb} confident in {dex} for secure {noun} {verb}",
        "If {verb} {noun} is your goal, {dex} is the {adjective} way",
        "Truly {adjective}, {dex} has streamlined how I {verb} {noun}",
        "A {adjective} player in the {noun} {verb} market, that’s {dex}",
        "Remarkably {adjective}, {dex} simplifies {noun} {verb}",
        "I {adverb} recommend {dex} for anyone into {noun} {verb}",
        "With {dex}, {noun} {verb} is no longer a hassle",
        "The {adjective} features of {dex} make {noun} {verb} a breeze",
        "I trust {dex} for all my {adjective} {noun} {verb} needs",
        "Innovation in {noun} {verb}? That’s {dex} for you",
        "Thanks to {dex}, I now {verb} my {noun} {adverb} and {adjective}",
        "Never knew {noun} {verb} could be this {adjective} until I found {dex}",
        "{dex} is redefining {adjective} {noun} {verb} for everyone",
        "For top-notch {noun} {verb}, I always choose {dex}",
        "{dex}: Where {adjective} {noun} {verb} meets innovation",
        "I rely on {dex} for {adjective}, hassle-free {noun} {verb}",
        "Turning to {dex} for {noun} {verb} was the best decision I made",
        "A leader in {adjective} {noun} {verb} - that's {dex} for you",
        "The {dex} is {adjective}, {verb} {noun} {adverb}",
        "Using {dex} to {verb} {noun} was a {adjective} experience",
        "I found {verb} {noun} with {dex} {adverb} {adjective}",
        "{dex} makes {noun} {verb} {adverb} {adjective}",
        "A truly {adjective} way to {verb} {noun} is via {dex}",
        "Never going back after trying {dex} for {verb} {noun}",
        "Changed my {noun} {verb} game, thanks to {dex}'s {adjective} system",
        "{dex} has been a {adjective} solution for my {noun} {verb} needs",
        "I'm {adverb} impressed with how {adjective} {dex} is for {verb} {noun}",
        "For {noun} {verb}, nothing beats the {adjective} experience of {dex}",
        "Finding {dex} was like striking gold in the world of {noun} {verb}",
        "The {adjective} interface of {dex} made {verb} my {noun} a pleasure",
        "What sets {dex} apart is its {adjective} approach to {noun} {verb}",
        "I was {adverb} amazed by the {verb} speed on {dex}",
        "{dex} excels in {noun} {verb} with its {adjective} and {adverb} seamless process",
        "The ease of {verb} {noun} on {dex} cannot be overstated; it's {adjective}",
        "I’ve been {adverb} impressed with the {noun} {verb} capabilities of {dex}",
        "Every {noun} {verb} transaction on {dex} has been {adjective} and {adverb} effortless",
        "I always recommend {dex} for anyone needing {adjective} {noun} {verb}",
        "{dex} is the epitome of {adjective} {noun} {verb} in this digital age",
        "For {adjective} {verb} of {noun}, my choice is always {dex}",
        "Can't get over how {adjective} {verb} {noun} is with {dex}",
        "The {dex} platform: a {adjective} blend of technology and user experience",
        "I'm {adverb} sold on {dex}'s {adjective} features for {noun} {verb}",
        "In a league of its own, {dex} transforms {noun} {verb} into a {adjective} task",
        "Every aspect of {noun} {verb} is {adverb} improved by using {dex}",
        "{dex} has set a new benchmark for {adjective} {noun} {verb}",
        "Joining {dex} was the best decision for my {noun} {verb} activities",
        "The {noun} {verb} process on {dex} is as {adjective} as it gets",
        "Gone are the days of complicated {noun} {verb}, thanks to {dex}",
        "Kudos to {dex} for making {noun} {verb} so {adverb} {adjective}",
        "I've never seen anything as {adjective} for {noun} {verb} as {dex}",
        "The {noun} {verb} revolution starts with {dex} – it’s that {adjective}",
        "A {adjective} {noun} {verb} journey is guaranteed with {dex}",
        "Time and again, {dex} proves why it's the best for {noun} {verb}",
        # Short templates with placeholders
        "{adjective} {dex} experience",
        "{dex} rocks for {noun}",
        "{verb} {noun} with {dex}? {adjective}",
        "{dex} = {adjective} {verb}",
        "Just {verb} with {dex}, {adjective}",
        "Nothing but {adjective} things to say about {dex}",
        "My go-to for {noun} {verb}: {dex}",
        "{dex}'s {adjective} - love it",
        "Trust {dex} for {adjective} {verb}",
        "Always {adjective} with {dex}",
        "Love {dex}'s simplicity",
        "{dex} is a {noun} {verb} powerhouse",
        "So {adjective} and easy - thanks {dex}",
        "{dex} = {noun} {verb} made easy",
        "All about {dex} for {noun}",
        "Effortless and {adjective} with {dex}",
        "My {noun} {verb} go-to: {dex}",
        "{adjective} {verb} thanks to {dex}",
        "Trust in {dex} always pays off",
        "{dex} never disappoints",
        "{adjective} {verb} with {dex} only",
        "Always a win with {dex}",
        "{dex}: {adjective} every time",
        "Can't beat {dex} for {noun}",
        "My {noun} {verb} hero? {dex}",
        "Rely on {dex} for {verb}",
        "Simply {adjective} - that's {dex}",
        "{dex} always delivers",
        "Top {verb} choice? {dex}",
        "Making {noun} {verb} great: {dex}",
        "{dex}: Always a {adjective} choice",
        "Count on {dex} for {noun}",
        "The {noun} {verb} leader: {dex}",
        "Choose {dex}, choose {adjective}",
        "Forever loyal to {dex}",
        "Just perfect - {dex}",
        "{dex} makes life easier",
        "Always a {adjective} time with {dex}",
        "{dex} = {noun} {verb} success",
        "{noun} {verb} simplified, thanks {dex}",
        "So glad I found {dex}",
        "{dex}, you're the best",
        "All about that {dex} life",
        "Big fan of {dex} here",
        "{dex} is the future",
        "{dex} for the win",
        "Simply loving {dex}",
        "{noun} {verb}? {dex} it",
        "Impressed by {dex}",
        "{dex} exceeded expectations",
        "Can't beat the {dex} experience",
        "{dex} nailed it",
        "My {noun} {verb} go-to? {dex}",
        "Thank you, {dex}",
        "Always choosing {dex}",
        "{dex} all the way",
        "{dex} never fails to amaze",
        "Sticking with {dex}",
        "{dex}: Simply unmatched",
        "{adjective}, reliable - that's {dex}",
    ]

    adjectives = ['fast', 'secure', 'reliable', 'efficient', 'easy', 'amazing', 'innovative', 'user-friendly', 'revolutionary', 'groundbreaking', 'seamless', 'intuitive', 'cutting-edge', 'robust', 'dynamic', 'trustworthy', 'advanced', 'sophisticated', 'flexible', 'powerful', 'versatile', 'convenient', 'state-of-the-art', 'unparalleled', 'superior', 'profitable', 'lucrative', 'dependable', 'scalable', 'sustainable', 'profitable']
    adverbs = ['really', 'super', 'totally', 'incredibly', 'exceptionally', 'absolutely', 'extremely', 'remarkably', 'extraordinarily', 'highly', 'exceptionally', 'astonishingly', 'significantly', 'profoundly', 'immensely', 'vastly', 'tremendously', 'spectacularly', 'amazingly', 'astoundingly', 'dramatically', 'fantastically', 'notably', 'strikingly', 'remarkably', 'exceedingly', 'surprisingly', 'phenomenally', 'significantly', 'impressively']
    verbs = ['trading', 'using', 'swapping', 'staking', 'sending', 'receiving', 'managing', 'investing', 'exchanging', 'accumulating', 'growing', 'diversifying', 'enhancing', 'optimizing', 'expanding', 'leveraging', 'mobilizing', 'elevating', 'upgrading', 'amplifying', 'maximizing', 'evolving', 'integrating', 'augmenting', 'broadening', 'safeguarding', 'enriching', 'empowering', 'streamlining', 'consolidating', 'fortifying']
    nouns = ['crypto', 'assets', 'tokens', 'funds', 'ETH', 'ether', 'holdings', 'funds']
    dex_names = ['this dex', 'this DEX', 'this dapp', 'this DAPP', dex_name, dex_name.upper(), dex_name.lower()]

    dex = random.choice(dex_names)
    adjective = random.choice(adjectives)
    adverb = random.choice(adverbs)
    verb = random.choice(verbs)
    noun = random.choice(nouns)

    if random.random() < 0.3:
        verb = verb.replace("ing", "in'") if "ing" in verb and random.random() < 0.5 else verb

    if random.random() < 0.15:
        typo_index = random.randint(0, len(adjective) - 1)
        typo_variations = ['', adjective[typo_index + 1], random.choice('aeiou'), adjective[typo_index].upper(), '']
        adjective = adjective[:typo_index] + random.choice(typo_variations) + adjective[typo_index + 1:]

    if random.random() < 0.1:
        noun, verb = verb, noun

    adverb = '' if random.random() < 0.2 else adverb

    template = random.choice(templates)
    review = template.format(dex=dex, adjective=adjective, adverb=adverb, verb=verb, noun=noun)

    review += random.choice(['.', '!', '...']) if random.random() < 0.8 else ''

    if random.random() < 0.01:
        casual_phrases = [
            'Honestly, ', 'No joke, ', 'Seriously, ', 'Trust me, ',
            'FYI, ', 'Can’t believe it, ', 'Wow, ', 'You know what? ',
            'Guess what? ', 'Here’s the thing: ', 'Honestly speaking, ',
            'No doubt, ', 'Let me tell you, ', 'Real talk, ', 'Just saying, ',
            'Hands down, ', 'On a real note, ', 'Not gonna lie, ',
            'Straight up, ', 'For real, ', 'In all honesty, ', 'If you ask me, ',
            'No kidding, ', 'Hear me out, ', 'Between you and me, '
        ]
        review = random.choice(casual_phrases) + review

    review = review if random.random() < 0.5 else review.capitalize()

    return review

async def make_review(address):
    try:
        headers = {
            'authority': 'dappsheriff.com',
            'accept': '*/*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://dappsheriff.com',
            'referer': 'https://dappsheriff.com/izumi',
            'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        }

        dapps = {
            214: 'Airswap', 174: 'FWDX'
        }
        dapp_id = random.choice(list(dapps.keys()))
        dapp_name = dapps[dapp_id]

        review = await generate_random_dapp_review(dapp_name)

        json_data = {
            'app_id': dapp_id,
            'reviewer': address,
            'review': review,
            'rate': random.choice([4, 5]),
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(f'https://dappsheriff.com/api/app/{dapp_id}/reviews', headers=headers, json=json_data) as response:
                if response.status == 200:
                    return True
                else:
                    await asyncio.sleep(random.uniform(1, 2))
                    raise Exception
    except Exception:
        return await make_review(address)

from web3.auto import w3


async def process_wallet(wallet, semaphore):
    try:
        res = await make_review(wallet)
        if res:
            print(f"{wallet} - DONE")
        else:
            print(f"{wallet} - ERROR")
    except Exception as e:
        print(f"{wallet} - ERROR: {e}")
    semaphore.release()


async def main():
    max_workers = 50
    semaphore = asyncio.Semaphore(max_workers)

    with open("wallets.txt", "r") as f:
        wallets = [w3.eth.account.from_key(row.strip()) for row in f]

    async def limited_concurrent_tasks(wallet):
        async with semaphore:
            await process_wallet(wallet, semaphore)

    tasks = [limited_concurrent_tasks(wallet.address) for wallet in wallets]

    await asyncio.gather(*tasks, return_exceptions=True)

asyncio.run(main())