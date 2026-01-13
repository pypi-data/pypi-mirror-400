# AIForge

**AIForge** è un sistema **bidirezionale** per trasformare output disordinati di AI (ChatGPT, Claude, Mistral) in progetti software strutturati e mantenibili, e viceversa. Supporta **Flutter, Python, Node.js, TypeScript, Java, C#**, con gestione avanzata dei conflitti, ottimizzazione per limiti di token, e integrazione con Git e modelli locali.

---

## 🚀 Installazione

### Base (solo CLI)
```bash
pip install aiforge
```

### Con supporto per modelli locali
```bash
pip install aiforge[local-ai]
```

### Per sviluppo
```bash
git clone https://github.com/tuo-username/AIForge.git
cd AIForge
pip install -e .[dev,local-ai]
```

---

## 🛠 Funzionalità

| Comando               | Descrizione                                      | Esempio                                                                 |
|-----------------------|--------------------------------------------------|-------------------------------------------------------------------------|
| `ai2project`          | Da dump AI a progetto strutturato               | `aiforge ai2project dump.txt my_project --mode clean`                 |
| `project2ai`          | Da progetto a file AI-friendly                   | `aiforge project2ai my_project export.md --max-tokens 4000`           |
| `sync`                | Sincronizza progetto con nuovo output AI       | `aiforge sync new_dump.txt my_project --mode patch --non-interactive`|
| `validate`            | Valida la struttura del progetto                | `aiforge validate my_project`                                          |
| `init-git`            | Configura hooks Git per validazione automatica | `aiforge init-git my_project`                                          |
| `refine`              | Migliora un progetto con AI locale             | `aiforge refine my_project --model mistralai/Mistral-7B-Instruct-v0.1` |

---

## 📦 Esempi d'Uso

### 1. Da AI a Progetto
```bash
aiforge ai2project dump.txt my_flutter_project --mode clean
```

### 2. Sincronizzazione con Gestione Conflitti
```bash
aiforge sync new_dump.txt my_project --mode patch --non-interactive
```

### 3. Raffinamento con AI Locale
```bash
aiforge refine my_project --model mistralai/Mistral-7B-Instruct-v0.1
```

---

## 🔧 Integrazione con Git
AIForge include **pre-commit hooks** per validare automaticamente il progetto prima di ogni commit:
```bash
aiforge init-git my_project
```

---

## 📂 Struttura di un Progetto AIForge
```
my_project/
├── lib/
│   ├── main.dart
│   └── utils.dart
├── pubspec.yaml
└── .git/
    └── hooks/
        └── pre-commit  # Hook automatico per validazione
```

---

## 🤖 Supporto per Modelli Locali
AIForge supporta modelli come:
- **Mistral-7B**
- **Llama2-70B**
- **CodeLlama**

Esempio di raffinamento con modello locale:
```bash
aiforge refine my_project --model mistralai/Mistral-7B-Instruct-v0.1
```

---

## 🧪 Test
Esegui i test con:
```bash
pytest tests/
```

---

## 🤝 Contribuire
1. Forka il repository.
2. Crea un branch: `git checkout -b feature/nome-feature`.
3. Committa le modifiche: `git commit -m "Aggiunta feature"`.
4. Pusha il branch: `git push origin feature/nome-feature`.
5. Apri una Pull Request.

---

## 📄 Licenza
MIT
