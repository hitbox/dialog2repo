# dialog2repo

**Track changes to Linus Åkesson's Dialog releases using a Git repository.**

[Linus' Dialog Project](https://linusakesson.net/dialog/index.php)

This project, dialog2repo, is not complete or working.

---

## Plan
- **Scrape Web Page for Release Links**
  - Implemented in `scrape_links.py`.
  - Parses the site for links to new Dialog releases.

- **Verify Remote Files**
  - Optionally, hash remote files and compare them to previously downloaded versions to detect changes.

- **Handle Different File Types**
  - Releases may include ZIP archives or other formats.

- **Organize Downloads**
  - Determine the correct destination for downloaded files by referencing existing files or structures.

- **Commit in Release Order**
  - Use the order of HTML list items on the site to determine the sequence of commits.

- **File Tracking and Management**
  - Implement file tracking logic in `file_tracker.py`.
  - Manage file movements, unzipping, and placement into the final Dialog repository.

- **Interactive Integration**
  - Provide an option to manually unzip or move new files to the Dialog repo directory, followed by automatic Git commits.

