# RenameIt CLI

A simple, safe, and efficient **CLI tool** to rename files and folders in bulk with **undo support**. Perfect for organizing your files with minimal effort.  

---

## About the Developer

**Muhammad Ammar Ali** – a passionate Computer Information Technology student and self-taught AI enthusiast.  

- 🎓 Currently pursuing a **3-year diploma in Computer Information Technology at Christian Technical Training Center**
- 💻 Self-studying **Artificial Intelligence, Machine Learning, and Deep Learning**  
- 🤖 Experienced in building **automation workflows, AI agents, and Python projects**  
- 🔧 Skilled in **Python programming**, **CLI tools**, and **n8n automation**  

---

## Features

- Bulk rename **files** and **folders** in a single command  
- Add **custom base names** or numbering automatically  
- **Undo** the last batch rename safely  
- Easy-to-use **CLI interface**  
- Cross-platform support (Windows/Linux/Mac)  

---

## Installation

Install directly from PyPI:

```bash
pip install renameit-cli
````

---

## Usage

### Rename files

```bash
renameit rename -pt "C:\Users\ammar\Downloads\Doraemon S1" -fl PPT
```

### Rename folders

```bash
renameit rename -pt "C:\Users\ammar\Downloads\Doraemon S1" -fd Season
```

### Undo last rename

```bash
renameit undo
```

> Note: Undo works only for the **latest batch rename**. After an undo, a new rename will overwrite the history.

---

## Example

Before:

```
C:\Test
├─ file1.txt
├─ file2.txt
```

Command:

```bash
renameit rename -pt "C:\Test" -fl Document
```

After:

```
C:\Test
├─ 1_Document.txt
├─ 2_Document.txt
```

Undo:

```
renameit undo
```

Files restored to original names.

---

## Roadmap

* Dry-run mode (`--dry-run`)
* Regex-based renaming and advanced numbering
* Multi-level undo support
* Config file for default naming patterns
* Optional GUI wrapper

---

## Contact & Links

* GitHub: Coming Soon---!
* LinkedIn: [https://www.linkedin.com/in/m-ammarali/](https://www.linkedin.com/in/m-ammarali/)

---

## License

MIT License © 2026 Ammar

