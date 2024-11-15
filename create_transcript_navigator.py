"""This script is a helper for qualitative evaluation of games.

It creates a big html file (size depending on the arguments specified).
The file contains a list of paths to all transcript files present in the
specified results directory.

Usage of Output:
    When opening the html file in a browser you will get two buttons 'next'
    and 'previous' to navigate through the episodes one after the other.

    Be aware that your progress is not saved when closing the browser.
    Tipp: Don't create one huge transcript_navigator.html for all episodes,
    but one for each game and language.

Arguments:
    Games, languages or episodes to be included in the output file can be
    specified in the if __name__ block.

Supported games and result types:
    - The script is not game specific but only tested with the imagegame and
      referencegame.
        - I used it only for the imagegame since it's multi-turn. For
          the qualitative analysis of the referencegame there is also the script
          'create_excel_overview.py' which gives a faster overview.
    - It should work with multilingual and monolingual results folders. But was
      developed primarily for multilingual results.

"""


import glob
import re

from evaluation.create_excel_overview import natural_sort_key

HTML_HEAD = """
<!DOCTYPE html>
<html>
<head>
    <title>Navigator</title>
</head>
<body>
    <h1></h1>
    <div id="transcript-links">
"""

TRANSCRIPT_LINK = """
        <a style="display: none;" target="transcript-frame" href="{}">Next episode</a>
"""

HTML_TAIL = """
    </div>

    <!-- Iframe zum Anzeigen der Transcripts -->
    <iframe id="transcript-frame" name="transcript-frame" width="90%" height="600px"></iframe>

    <script>
        const transcript_links = document.getElementById("transcript-links").getElementsByTagName("a");

        transcript_links[0].style.display = "block";

        for (const link of transcript_links) {
            link.addEventListener("click", function () {
                this.style.display = "none";
                let prev = this.previousElementSibling;
                let next = this.nextElementSibling;
                if (prev) {
                    prev.style.display = "block";
                    prev.innerHTML = "Previous episode";
                    let preprev = prev.previousElementSibling;
                    if (preprev) {
                        preprev.style.display = "none";
                        preprev.innerHTML = "Next episode";
                    }
                }
                if (next) {
                    next.style.display = "block";
                    next.innerHTML = "Next episode";
                    let afternext = next.nextElementSibling;
                    if (afternext) {
                        afternext.style.display = "none";
                        afternext.innerHTML = "Next episode";
                    }
                }
            });
        }
    </script>

</body>
</html>
"""


def get_transcript_htmls(results_path, games, languages=None, episode_sample=None):
    """Get transcript paths.

    Args:
        results_path (str): The results folder.
        games (list[str]): List of games. Can't be empty.
        languages (list[str]): List of language identifiers. If empty/None, includes all.
            Should also be None when the results_path folder is monolingual.
        episode_sample (list[int]): List of episodes given as integers. If empty/None, includes all.
            Useful when you don't want to look through all episodes, but just get an overview.

    Returns:
        list: Flat list of all paths.

    """
    filename = "transcript.html"
    paths_per_game = []
    for game in games:
        paths = glob.glob(f"{results_path}/**/{game}/**/{filename}", recursive=True)
        paths = sorted(paths, key=natural_sort_key)
        if languages:
            paths = [path for path in paths
                     if re.search(f"{results_path}/(\w+)/", path).group(1) in languages]
        if episode_sample:
            paths = [path for path in paths
                     if int(re.search("episode_(\d*)", path).group(1)) in episode_sample]
        paths_per_game.append(paths)
    paths_per_game = [path for game in paths_per_game for path in game]
    return paths_per_game


if __name__ == "__main__":
    # Example run (change arguments if needed):
    results_path = "results/v1.5_multiling"
    games = ["imagegame"]  # "imagegame" "referencegame"
    languages = ["en", "es", "ru", "te", "tk", "tr"]
    file_out = "transcript_navigator_imagegame_human.html"

    # Extract paths to transcript.html's
    transcript_paths = get_transcript_htmls(results_path, games, languages=languages)

    # Build html
    html = HTML_HEAD
    for path in transcript_paths:
        html_link = TRANSCRIPT_LINK.format(path)
        html += html_link
    html += HTML_TAIL

    # Save
    with open(file_out, "w") as file:
        file.write(html)
