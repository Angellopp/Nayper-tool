import os

from datetime import datetime
from harwest.lib.utils import config


class Submissions:
  def __init__(self, submissions_directory, user_data):
    self.user_data = user_data
    self.table_svg_path = os.path.join(submissions_directory, "table.svg")
    self.readme_path = os.path.join(submissions_directory, "README.md")
    self.submission_json_path = \
      os.path.join(submissions_directory, "submissions.json")
    self.store = config.load_submissions_data(self.submission_json_path)

  def add(self, submission):
    submission_id = submission['submission_id']
    self.store[str(submission_id)] = submission
    self.__generate_readme(list(self.store.values()))
    config.write_submissions_data(self.submission_json_path, self.store)

  def contains(self, submission_id):
    return str(submission_id) in self.store

  def __generate_profile(self):
    profile = ""
    for platform in [("Codeforces", "https://codeforces.com/profile/{handle}"),
                     ("AtCoder", "https://atcoder.jp/users/{handle}")]:
      if platform[0].lower() not in self.user_data:
        continue
      handle_name = self.user_data[platform[0].lower()]
      svg_url = "https://raw.githubusercontent.com/rahuldkjain/github-profile-readme-generator/master/src/images/icons/Social/{platform}.svg".format(
        platform=platform[0].lower(),
        handle=handle_name,

      )
      profile_url = platform[1].format(handle=handle_name)
      profile += "* {platform} &nbsp; <a href='{profile_url}'><img src='{svg_url}' width='{width}' height='{height}'></a>\n".format(
        platform=platform[0],
        profile_url=profile_url,
        svg_url=svg_url,
        width=25,
        height=25
      )
    return profile

  def __generate_readme(self, submissions):
    submissions = sorted(
      submissions,
      key=lambda s: (-s['contest_id'], s['problem_index']),
    )
    index = len(set([x['problem_url'] for x in submissions]))
    xedni = 0
    problems = set()
    rows = []
    curr = -1
    for idx, submission in enumerate(submissions):
      if submission['problem_url'] in problems:
        continue
      problems.add(submission['problem_url'])
      row = "        <tr class='light'>\n" if xedni % 2 == 0 else "        <tr class='dark'>\n"
      row += "          <td " 
      if idx == 0:
        row += "class='tole' "
      if index == 1:
        row += "class='bole' "
      row += "align='center'>{index}</td>\n".format(index=index)
      if submission['contest_id'] != curr: 
        aux = idx
        curr = submission['contest_id']
        letters = set()
        while aux < len(submissions) and submissions[aux]['contest_id'] == curr:
          letters.add(submissions[aux]['problem_index'])
          aux += 1
        row += "          <td rowspan='{rep}' align='center'>{contest_id}</td>\n".format(
          rep=len(letters),
          contest_id=submission['contest_id']
        )

      row += "          <td class='name' align='left'><a href='{problem_url}'>{problem_index} - {problem_name}</a></td>\n".format(
        problem_index=submission['problem_index'],
        problem_name=submission['problem_name'],
        problem_url=submission['problem_url']
      )
      row += "          <td align='center'><a class='solution' href='{path}'>{rating}</a></td>\n".format(
        # path=submission['path'].replace('\\', '/'),
        path=submission['submission_url'],
        rating=submission['tags'][-1].replace('*', '') if submission['tags'] and submission['tags'][-1].startswith('*') else '?'
      )
      row += "          <td "
      if idx == 0:
        row += "class='tori' "
      if index == 1:
        row += "class='bori' "
      row += "align='center'><div style='display: flex; justify-content: center;'>{tags}</div></td>\n".format(
        tags=' '.join(['<code>{tag}</code>'.format(tag=x) for x in submission['tags'] if not x.startswith('*')])
      )
      row += "        </tr>"
      rows.append(row)
      index -= 1
      xedni += 1

    template_table = open(str(config.RESOURCES_DIR.joinpath("table.template")), 'r',
                    encoding="utf-8").read()
    style = open(str(config.RESOURCES_DIR.joinpath("style.css")), 'r', encoding="utf-8").read()
    table_data = template_table.format(
      height_placeholder=40+57 * len(rows),
      style_placeholder=style,
      submission_placeholder="\n".join(rows))
    with open(self.table_svg_path, 'w', encoding="utf-8") as fp:
      fp.write(table_data)

    template_readme = open(str(config.RESOURCES_DIR.joinpath("readme.template")), 'r',
                    encoding="utf-8").read()
    readme_data = template_readme.format(
      table_url_placeholder=config.get_remote_url().replace('https://github.com/', 'https://raw.githubusercontent.com/').replace('.git', '') + "/master/table.svg",
      height_placeholder=40+57 * len(rows),
      profile_placeholder=self.__generate_profile()
    )
    with open(self.readme_path, 'w', encoding="utf-8") as fp:
      fp.write(readme_data)
    
