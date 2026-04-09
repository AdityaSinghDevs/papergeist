from utils.file_utils import read_json, write_json
from utils.config_loader import load_cfg

cfg = load_cfg("configs/config.yaml")

def filter_new_papers(papers, user_id):
    sent_data = read_json(cfg["paths"]["sent_file"], {})

    user_sent = set(sent_data.get(str(user_id), []))

    new_papers = [p for p in papers if p["id"] not in user_sent]

    # update only this user's history
    for p in new_papers:
        user_sent.add(p["id"])

    sent_data[str(user_id)] = list(user_sent)
    write_json(cfg["paths"]["sent_file"], sent_data)

    return new_papers[:cfg["app"]["papers_per_day"]]