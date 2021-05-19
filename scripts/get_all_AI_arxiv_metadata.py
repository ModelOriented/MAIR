import json

arixv_metadata_filepath = "data/citation_graph/arxiv-metadata-oai-snapshot.json"
ARXIV_CATEGORIES_PATH_INPUT = "data/arxiv_dump/arxiv_AI_narrow_categories.txt"
arxiv_ai_metadata_path = "data/citation_graph/arxiv-ai-metadata.json"

def get_categories():
    categories = set()
    with open(ARXIV_CATEGORIES_PATH_INPUT, "r") as f:
        for line in f:
            categories.add(line.split(" ")[0])
    return categories


def filter_category(AI_categories: set, paper_categories: set):
    return len(AI_categories.intersection(paper_categories)) > 0

def change_authors_format(authors):
    return [{"name": ' '.join(name).strip()} for name in authors]

if __name__ == "__main__":
    AI_categories = get_categories()
    with open(arixv_metadata_filepath, "r") as f:
        filtered_entries = dict()
        for i, d in enumerate(f):
            if (i + 1) % 1000 == 0:
                print(i)
            metadata = json.loads(d)
            if filter_category(AI_categories, set(metadata['categories'].split(' '))):
                filtered_entries['http://arxiv.org/abs/{}'.format(metadata['id'])] = {
                    'id': metadata['id'],
                    'title': metadata['title'],
                    'authors': change_authors_format(metadata['authors_parsed'])
                }
    print(len(filtered_entries))
    with open(arxiv_ai_metadata_path, "w") as f:
        json.dump(filtered_entries, f, indent=2, ensure_ascii=False)

