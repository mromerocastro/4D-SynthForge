# 🚀 Quick Start Guide - 4D-SynthForge

## Setup (5 minutos)

### 1. Instalar Dependencias

```powershell
# En la carpeta del proyecto
pip install -r requirements.txt
```

### 2. Configurar API Key de Gemini

```powershell
# Obtén tu key en: https://aistudio.google.com
$env:GEMINI_API_KEY = "AIzaSy..."
```

### 3. Crear Video de Demo

```powershell
python demo_video_creator.py
```

Esto crea `examples/ball_cup.mp4` (5 segundos, pelota golpea taza)

---

## Uso Básico

### Opción 1: Pipeline Completo (Sin Rendering)

```powershell
# Analiza video + genera 9 variaciones
python main.py examples/ball_cup.mp4 --count 9
```

**Salida:**
- `output/ball_cup_analysis.json` - Análisis de Gemini
- `output/variations/variation_*.json` - 9 variaciones
- `output/usd_scenes/variation_*.py` - Scripts para Isaac Sim

### Opción 2: Paso a Paso

```powershell
# 1. Analizar video con Gemini
python video_analyzer.py examples/ball_cup.mp4

# 2. Generar código Isaac Sim
python code_generator.py output/ball_cup_analysis.json

# 3. Crear variaciones
python domain_randomizer.py output/ball_cup_analysis.json 100
```

---

## Con Isaac Sim (Si lo tienes instalado)

```powershell
# Pipeline completo con rendering
python main.py examples/ball_cup.mp4 --count 9 --render
```

O ejecutar script manualmente:

```bash
# Linux/Mac
~/.local/share/ov/pkg/isaac_sim-*/python.sh output/usd_scenes/variation_001.py

# Windows
"%USERPROFILE%\.local\share\ov\pkg\isaac_sim-*\python.bat" output/usd_scenes/variation_001.py
```

---

## Demo para Hackathon

### Script de Presentación (3 minutos)

**Diapositiva 1: El Problema** (30 seg)
- "Entrenar IA requiere datos masivos"
- "Recolectar datos reales = $$$"

**Diapositiva 2: La Magia** (1 min)
```powershell
# Muestra el video
python demo_video_creator.py  # (ya creado)

# Analiza con Gemini
python video_analyzer.py examples/ball_cup.mp4
```

*Muestra el JSON:*
```json
{
  "physics": {
    "mass": 0.5,
    "velocity": {"x": 2.0},
    "restitution": 0.7
  }
}
```

**"¡Gemini entendió la física desde pixeles!"**

**Diapositiva 3: La Multiplicación** (1 min)
```powershell
python main.py examples/ball_cup.mp4 --count 9
```

*Muestra carpeta `output/variations/`:*
- 9 archivos JSON con diferentes colores, luces, física

**"De 1 video → 100 ejemplos únicos para entrenar IA"**

**Diapositiva 4: El Valor** (30 seg)
- ✅ Mercado de datos sintéticos: $3.5B
- ✅ Usa Isaac Sim (profesional)  
- ✅ Seguro (solo objetos geométricos)

---

## Estructura de Archivos Generados

```
output/
├── ball_cup_analysis.json        # Gemini output
├── variations/
│   ├── variation_000.json        # Color azul, luz brillante
│   ├── variation_001.json        # Color rojo, luz normal
│   └── ...
└── usd_scenes/
    ├── base_scene.py             # Escena original
    ├── variation_000.py          # Script Isaac Sim #1
    └── ...
```

---

## Troubleshooting

### "Gemini API key not found"
```powershell
$env:GEMINI_API_KEY = "tu-api-key-aquí"
```

### "Isaac Sim not found"
- Instala desde: https://developer.nvidia.com/isaac-sim
- O usa `--count 9` sin `--render` (solo genera scripts)

### "opencv-python not found"
```powershell
pip install opencv-python
```

---

## Próximos Pasos

1. **Probar con tu propio video:**
   ```powershell
   python main.py tu_video.mp4 --count 100
   ```

2. **Ajustar randomización** en `config.py`:
   ```python
   RANDOMIZATION_CONFIG = {
       "material": {"base_color_hue": (0.0, 1.0)},
       "lighting": {"dome_intensity": (500, 3000)},
       # etc...
   }
   ```

3. **Integrar con Houdini** (futuro):
   - Los archivos USD son compatibles
   - Importar en Houdini para VFX avanzados

---

## Recursos

- 📖 README completo: `README.md`
- 🎓 Walkthrough técnico: Ver artifacts en la conversación
- 🔧 Código fuente: Todos los `.py` están documentados
- 🌐 Gemini API: https://aistudio.google.com
- 🎮 Isaac Sim: https://developer.nvidia.com/isaac-sim

---

**¡Listo para el hackathon! 🏆**

*De realidad → simulación → infinito*
