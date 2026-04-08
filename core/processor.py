from utils.file_utils import read_json, write_json
from utils.config_loader import load_cfg

cfg = load_cfg("configs/config.yaml")
def filter_new_papers(papers):
    sent = set(read_json(cfg["paths"]["sent_file"], []))

    new_papers = [p for p in papers if p["id"] not in sent]

    for p in new_papers:
        sent.add(p["id"])
    
    write_json(cfg["paths"]["sent_file"], list(sent))

    return new_papers[:cfg["app"]["papers_per_day"]]