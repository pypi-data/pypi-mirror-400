#!/usr/bin/python3

import xmltodict
import weltschmerz.anime as anime
import configparser
import argparse
import queue
import threading
import datetime
import os

from typing import List


class MyListParser:
    def __init__(self, db="sqlite:///:memory:"):
        self.dbs = anime.DatabaseSession(db, False)
        self.q_in = queue.Queue()
        self.q_out = queue.Queue()

    def parse_mylist_export_files(self, files: List[str], threads: int = 2):
        workers = {}

        for i in range(1, threads):
            workers[i] = threading.Thread(target=self.xml_parser)
            workers[i].daemon = True
            workers[i].start()
        for mylist_xml_file in files:
            self.q_in.put(mylist_xml_file)

        db_worker = threading.Thread(target=self.dict_to_mylist_anime_worker)
        db_worker.daemon = True
        db_worker.start()

        self.q_in.join()
        self.q_out.join()

    def dict_to_mylist_anime_worker(self):
        while True:
            anime_data = self.q_out.get()
            aired = try_parse_date(anime_data["anime"]["startdate"]["long"], "%d.%m.%Y")
            ended = try_parse_date(anime_data["anime"]["enddate"]["long"], "%d.%m.%Y")
            anime_anime = anime.Anime(
                aid=anime_data["anime"]["id"],
                year=anime_data["anime"]["year"],
                type=anime_data["anime"]["type"]["@id"],
                eps=anime_data["anime"]["count"]["@eps"],
                seps=anime_data["anime"]["count"]["@specials"],
                airdate=aired,
                enddate=ended,
                rating=not_empty(anime_data["anime"]["rating"]),
                votecount=not_empty(anime_data["anime"]["votes"]),
                tempvote=not_empty(anime_data["anime"]["tmprating"]),
                tempvcount=not_empty(anime_data["anime"]["tmpvotes"]),
                avgreview=not_empty(anime_data["anime"]["reviewrating"]),
                reviewcount=not_empty(anime_data["anime"]["reviews"]),
            )
            self.dbs.session.merge(anime_anime)
            # load anime from db to get related episodes etc.
            anime_anime = (
                self.dbs.session.query(anime.Anime)
                .filter(anime.Anime.aid == anime_data["anime"]["id"])
                .one()
            )
            anime_mylist_anime = anime.MylistAnime(
                aid=anime_data["anime"]["id"],
                ml_count_episodes=anime_data["anime"]["mylist_entry"]["count"]["@eps"],
                ml_count_specials=anime_data["anime"]["mylist_entry"]["count"][
                    "@specials"
                ],
                ml_count_total=anime_data["anime"]["mylist_entry"]["count"]["@total"],
                ml_watched_episodes=anime_data["anime"]["mylist_entry"]["watched"][
                    "@eps"
                ],
                ml_watched_specials=anime_data["anime"]["mylist_entry"]["watched"][
                    "@specials"
                ],
                ml_watched_total=anime_data["anime"]["mylist_entry"]["watched"][
                    "@total"
                ],
            )

            print(
                f"anime: {anime_mylist_anime.aid} - eps: {anime_mylist_anime.ml_count_episodes} - watched: {anime_mylist_anime.ml_watched_episodes}"
            )
            self.dbs.session.merge(anime_mylist_anime)
            # mylist export contains wishlisted anime,
            # so anime may have no episodes/files in mylist
            # resulting xml contains empty episodes element
            if not anime_data["anime"]["episodes"]:
                self.q_out.task_done()
                continue
            for episode in anime_data["anime"]["episodes"]["episode"]:
                try:
                    aired = datetime.datetime.strptime(
                        episode["aired"]["#text"], "%d.%m.%Y %H:%M"
                    )
                except ValueError:
                    aired = None
                try:
                    episode_update = datetime.datetime.strptime(
                        episode["update"]["#text"], "%d.%m.%Y %H:%M"
                    )
                except ValueError:
                    episode_update = None

                anime_episode = anime.Episode(
                    eid=episode["@id"],
                    aid=anime_data["anime"]["id"],
                    ep=episode["@number"],
                    airdate=aired,
                    length=episode["length"],
                    title_en=episode["name"],
                    last_update=episode_update,
                )
                if "name_kanji" in episode.keys():
                    anime_episode.title_jp = episode["name_kanji"]
                if "name_romaji" in episode.keys():
                    anime_episode.title_jp_t = episode["name_romaji"]
                self.dbs.session.merge(anime_episode)
                if self.dbs.session.dirty:
                    self.dbs.session.commit()
                for file in episode["files"]["file"]:
                    # generic files are 0 bytes
                    # skip them for now
                    if int(file["size_plain"]) == 0:
                        continue
                    # files containing multiple episodes have episode relations, can't track those atm
                    # skip them for now, when the current episode is from an ep relation
                    if (
                        file["eprelations"]
                        and "eprelation" in file["eprelations"].keys()
                        and len(file["eprelations"]["eprelation"]) >= 1
                    ):
                        if episode["@id"] in [
                            eprel["@eid"] for eprel in file["eprelations"]["eprelation"]
                        ]:
                            continue
                    try:
                        file_update = datetime.datetime.strptime(
                            episode["update"]["#text"], "%d.%m.%Y %H:%M"
                        )
                    except ValueError:
                        file_update = None
                    anime_file = anime.File(
                        fid=file["@id"],
                        filesize=file["size_plain"],
                        aid=anime_data["anime"]["id"],
                        eid=episode["@id"],
                        gid=file["group"]["@id"],
                        source=file["source"],
                        extension=file["filetype"],
                        hash_crc=file["hash_crc"] or None,
                        hash_md5=file["hash_md5"] or None,
                        hash_sha1=file["hash_sha1"] or None,
                        hash_tth=file["hash_tth"] or None,
                        hash_ed2k=file["hash_ed2k"]["key"],
                        last_update=file_update,
                    )
                    self.dbs.session.merge(anime_file)
                    if self.dbs.session.dirty:
                        self.dbs.session.commit()
                    try:
                        view_date = datetime.datetime.strptime(
                            file["viewdate"]["long"], "%d.%m.%Y %H:%M"
                        )
                    except ValueError:
                        view_date = None
                    anime_mylist_file = anime.MylistFile(
                        fid=file["@id"],
                        ml_state=file["mystate"]["@id"],
                        ml_viewed=file["state"]["iswatched"],
                        ml_viewdate=view_date,
                        ml_storage=file["storage"],
                        ml_source=file["source"],
                    )
                    self.dbs.session.merge(anime_mylist_file)
                    if self.dbs.session.dirty:
                        self.dbs.session.commit()
                    file_screenshots = (
                        self.dbs.session.query(anime.TitleScreenShot)
                        .filter(anime.TitleScreenShot.fid == anime_file.fid)
                        .all()
                    )
                    for file_screenshot in file_screenshots:
                        if (
                            file_screenshot.aid != anime_file.aid
                            or file_screenshot.eid != anime_file.eid
                        ):
                            file_screenshot.aid = anime_file.aid
                            file_screenshot.eid = anime_file.eid
                            self.dbs.session.merge(file_screenshot)
                            if self.dbs.session.dirty:
                                self.dbs.session.commit()

            print(
                f"anime: {anime_mylist_anime.aid} - eps: {anime_mylist_anime.ml_count_episodes} - watched: {anime_mylist_anime.ml_watched_episodes} done"
            )
            if self.dbs.session.dirty:
                self.dbs.session.commit()
            self.q_out.task_done()

    def xml_parser(self):
        while True:
            with open(self.q_in.get(), "r") as f:
                anime_xml = f.read()
                anime_data = xmltodict.parse(
                    anime_xml,
                    force_list=("episode", "file", "eprelation", "filerelation"),
                )
                self.q_out.put(anime_data)
                self.q_in.task_done()


def get_config(config_file=os.path.expanduser("~/.config/weltschmerz/weltschmerz.cfg")):
    config = configparser.ConfigParser()
    with open(config_file, "r", encoding="UTF-8") as cf:
        config.read_file(cf)

    parser = argparse.ArgumentParser(description="Import data from MyList export")
    parser.add_argument(
        "--database", help="database to use", default=config.get("client", "database")
    )
    parser.add_argument(
        "--log-file",
        dest="log_file",
        help="logfile to use",
        default=config.get("client", "log"),
    )
    parser.add_argument(
        "--mylist-xml-files",
        dest="mylist_xml_files",
        nargs="+",
        help="mylist export: xml-plain-full anime files to process",
    )

    args = parser.parse_args()
    return args


def try_parse_date(date_str: str, format_str: str):
    try:
        return datetime.datetime.strptime(date_str, format_str)
    except ValueError:
        return None


def not_empty(var):
    if var != "-" or "":
        return var
    else:
        return None


if __name__ == "__main__":
    config = get_config()
    mlp = MyListParser(db=config.db)
    mlp.parse_mylist_export_files(files=config.mylist_xml_files)
