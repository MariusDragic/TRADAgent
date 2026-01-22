# Guide de Résolution des Erreurs - TRADAgent

## ✅ Corrections Apportées

### Problème Initial
L'erreur "I'm having trouble generating the report due to an error in the JSON formatting" était causée par plusieurs problèmes :

1. **Structure MACD imbriquée** : Le stock analyst retourne `momentum.macd` comme un dictionnaire `{macd, signal, histogram}`, mais le report writer s'attendait à des valeurs plates.

2. **Parsing JSON fragile** : Le JSON pouvait être entouré de texte explicatif de l'agent, causant des erreurs de parsing.

3. **Gestion d'erreurs insuffisante** : Les messages d'erreur n'étaient pas assez informatifs.

### Solutions Implémentées

#### 1. Fonction `extract_json_from_text()` 
Ajoutée dans `/tradagent/tools/report_writer_tools.py` :

```python
def extract_json_from_text(text: str) -> dict:
    """
    Extract JSON from text that may contain additional content.
    Tries multiple strategies to find and parse JSON.
    """
    # Strategy 1: Try to parse the entire text as JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Strategy 2: Look for JSON between code blocks (```json ... ```)
    import re
    json_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    matches = re.findall(json_block_pattern, text, re.DOTALL)
    if matches:
        try:
            return json.loads(matches[0])
        except json.JSONDecodeError:
            pass
    
    # Strategy 3: Find the first { and last } and try to parse that
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        try:
            return json.loads(text[first_brace:last_brace + 1])
        except json.JSONDecodeError:
            pass
    
    # If all strategies fail, raise an error
    raise json.JSONDecodeError(
        "Could not extract valid JSON from text.",
        text,
        0
    )
```

**Avantages :**
- ✅ Extrait le JSON même s'il est entouré de texte
- ✅ Supporte les code blocks markdown (```json ... ```)
- ✅ Fallback intelligent avec 3 stratégies
- ✅ Messages d'erreur clairs

#### 2. Gestion de la Structure MACD Imbriquée

```python
# Handle MACD - can be a dict or flat values
macd_data = momentum.get("macd", {})
if isinstance(macd_data, dict):
    macd = macd_data.get("macd", 0.0)
    signal = macd_data.get("signal", 0.0)
    histogram = macd_data.get("histogram", 0.0)
else:
    # Fallback to flat structure
    macd = momentum.get("macd", 0.0)
    signal = momentum.get("signal", 0.0)
    histogram = momentum.get("histogram", 0.0)
```

**Avantages :**
- ✅ Supporte les deux formats (imbriqué et plat)
- ✅ Compatibilité avec les données réelles du stock analyst
- ✅ Fallback robuste

#### 3. Meilleure Gestion d'Erreurs

```python
try:
    analysis = extract_json_from_text(analysis_json)
except json.JSONDecodeError as e:
    return {
        "success": False, 
        "error": f"Invalid JSON format: {str(e)}",
        "received_text": analysis_json[:500]  # Show first 500 chars for debugging
    }
```

**Avantages :**
- ✅ Messages d'erreur détaillés
- ✅ Affiche les 500 premiers caractères reçus pour le debugging
- ✅ Facilite le diagnostic des problèmes

#### 4. Gestion de l'Encodage UTF-8

```python
subprocess.run(
    [...],
    encoding='utf-8',
    errors='replace',  # Replace invalid UTF-8 sequences
)
```

**Avantages :**
- ✅ Évite les crashes lors de la compilation LaTeX
- ✅ Remplace les caractères invalides au lieu de crasher

## 🧪 Tests de Validation

Deux scripts de test ont été créés pour valider les corrections :

### Test 1 : `test_new_logic.py`
Teste la structure de base avec des données mockées.

```bash
cd /home/marius/dev/TRADAgent
source .venv/bin/activate
python test_new_logic.py
```

**Résultat attendu :**
```
✅ All required keys present!
✅ Report generated successfully!
   PDF: reports/test_report.pdf
```

### Test 2 : `test_real_flow.py`
Teste le flux complet avec les vraies données du stock analyst.

```bash
cd /home/marius/dev/TRADAgent
source .venv/bin/activate
python test_real_flow.py
```

**Résultat attendu :**
```
✅ Complete flow successful!
   PDF: reports/AAPL_real_data_report.pdf
   Size: 135.88 KB
```

## 📊 Structure de Données Supportée

Le système supporte maintenant les deux formats :

### Format Plat (pour compatibilité)
```json
{
  "momentum": {
    "rsi_14d": 65.5,
    "rsi_interpretation": "Neutral",
    "macd": 2.5,
    "signal": 1.8,
    "histogram": 0.7,
    "momentum_bias": "Bullish"
  }
}
```

### Format Imbriqué (données réelles du stock analyst)
```json
{
  "momentum": {
    "rsi_14d": 15.65,
    "rsi_interpretation": "Oversold",
    "macd": {
      "macd": -5.92,
      "signal": -4.34,
      "histogram": -1.59
    },
    "momentum_bias": "Bearish"
  }
}
```

## 🚀 Utilisation du Système

### Workflow Complet

1. **Lancer l'application :**
```bash
cd /home/marius/dev/TRADAgent
source .venv/bin/activate
python main.py
```

2. **Demander une analyse avec rapport :**
```
CHAT > Analyze AAPL and generate a report
```

3. **Le système va :**
   - 📊 Collecter les données via le stock analyst
   - 🤖 Analyser et enrichir avec des interprétations
   - 📄 Générer automatiquement le PDF avec f-strings
   - ✅ Sauvegarder dans `./reports/AAPL_report.pdf`

### Vérifier le Rapport Généré

```bash
ls -lh reports/AAPL_report.pdf
# Devrait afficher un fichier de ~135 KB

# Ouvrir le PDF
xdg-open reports/AAPL_report.pdf  # Linux
# ou
open reports/AAPL_report.pdf      # macOS
```

## 🔍 Debugging

Si vous rencontrez toujours des erreurs :

### 1. Vérifier le JSON retourné par le stock analyst

Ajoutez un print dans `main.py` après l'analyse :

```python
analysis_json = extract_final_answer(analysis_response)
print("\n🔍 DEBUG - Analysis JSON:")
print(analysis_json)
print("\n" + "=" * 60)
```

### 2. Tester manuellement le tool

```python
from tradagent.tools.report_writer_tools import generate_report_from_analysis
import json

# Votre JSON d'analyse
analysis = {...}

result = generate_report_from_analysis.invoke({
    "analysis_json": json.dumps(analysis)
})

print(result)
```

### 3. Vérifier les logs LaTeX

Si le PDF n'est pas généré, vérifiez les fichiers `.log` dans `./reports/` :

```bash
cat reports/AAPL_report.log
```

## 📝 Checklist de Résolution

- [x] Fonction `extract_json_from_text()` ajoutée
- [x] Gestion de la structure MACD imbriquée
- [x] Meilleure gestion d'erreurs avec messages détaillés
- [x] Gestion de l'encodage UTF-8
- [x] Tests passent avec succès
- [x] Documentation complète

## 🎯 Résultat Final

Le système est maintenant **robuste** et **flexible** :

✅ Accepte du JSON pur ou du JSON entouré de texte  
✅ Supporte les structures imbriquées et plates  
✅ Messages d'erreur clairs et informatifs  
✅ Génération de PDF fiable avec f-strings  
✅ Tests validés avec données réelles  

---

**Date :** 2026-01-22  
**Version :** 2.1  
**Status :** ✅ Résolu et Testé
