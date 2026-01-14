"""dspy Programs for Impostor Game."""

import logging

import dspy

from base import Program
from config import get_gpt_5_mini

logger = logging.getLogger(__name__)


class NPC(Program):
    """Program for AI players to say a word related to the keyword or category."""

    def __init__(self, lm: dspy.LM = None, seed: int = 42):
        super().__init__(lm=lm or get_gpt_5_mini(), seed=seed)

        class NPCSignature(dspy.Signature):
            role: str = dspy.InputField(desc="Tu rol: 'jugador' o 'impostor'")
            secret_info: str = dspy.InputField(desc="Palabra clave si eres jugador, categoria si eres impostor")
            words_said: str = dspy.InputField(desc="Palabras dichas por cada jugador hasta ahora")
            player_names: str = dspy.InputField(desc="Nombres de todos los jugadores en orden")
            
            reasoning: str = dspy.OutputField(desc="Tu razonamiento sobre qué palabra decir")
            word: str = dspy.OutputField(desc="UNA sola palabra relacionada")

        game_explanation = """
EL JUEGO: Adivina El Impostor

En este juego, hay varios jugadores alrededor de una mesa. A la mayoría se les asigna una PALABRA CLAVE secreta (todos tienen la misma palabra). A uno se le asigna el rol de IMPOSTOR, quien solo conoce la CATEGORÍA de la palabra, no la palabra en sí.

El objetivo es que los jugadores identifiquen al impostor votando, mientras el impostor intenta pasar desapercibido.

Cómo funciona:
1. Cada jugador dice UNA palabra relacionada con su información (palabra clave o categoría)
2. Los jugadores analizan las palabras para identificar quién podría ser el impostor
3. Se vota para eliminar a quien se cree que es el impostor
4. Si eliminan al impostor, ganan los jugadores. Si eliminan a un jugador normal, gana el impostor.

═══════════════════════════════════════════════════════════════════════════════
REGLA CRÍTICA - TIPO DE PALABRAS PERMITIDAS
═══════════════════════════════════════════════════════════════════════════════

⚠️ REGLA FUNDAMENTAL: NUNCA digas otra palabra que pertenezca a la misma categoría.

SIEMPRE debes decir:
- Características físicas (color, tamaño, forma, textura)
- Cualidades o propiedades (dulce, ácido, suave, fuerte, rápido, lento)
- Sensaciones o emociones asociadas (refrescante, reconfortante, emocionante)
- Usos o acciones relacionadas (comer, beber, jugar, usar, montar)
- Contextos o asociaciones (verano, invierno, fiesta, trabajo, casa)
- Verbos relacionados (ladrar, volar, nadar, cocinar, construir)

NUNCA digas:
- Otra palabra de la misma categoría
- Ejemplo: Si la categoría es "Frutas" y la palabra secreta es "Fresa", NO digas "manzana", "plátano", "naranja" (son otras frutas)
- Ejemplo: Si la categoría es "Animales" y la palabra secreta es "Perro", NO digas "gato", "león", "tigre" (son otros animales)

EJEMPLOS CONCRETOS:

Ejemplo 1 - Categoría "Frutas", Palabra secreta "Fresa":
  ✅ CORRECTO: "roja", "pequeña", "dulce", "primavera", "batido", "vitamina", "jugosa", "verano"
  ❌ INCORRECTO: "manzana", "plátano", "naranja", "uva" (son otras frutas de la misma categoría)

Ejemplo 2 - Categoría "Animales", Palabra secreta "Perro":
  ✅ CORRECTO: "fiel", "ladrar", "paseo", "collar", "amigo", "doméstico", "cola", "huella"
  ❌ INCORRECTO: "gato", "león", "tigre", "oso" (son otros animales de la misma categoría)

Ejemplo 3 - Categoría "Deportes", Palabra secreta "Fútbol":
  ✅ CORRECTO: "balón", "gol", "equipo", "cancha", "portería", "penal", "campeonato", "hincha"
  ❌ INCORRECTO: "tenis", "básquetbol", "natación", "voleibol" (son otros deportes de la misma categoría)

Ejemplo 4 - Categoría "Profesiones", Palabra secreta "Doctor":
  ✅ CORRECTO: "estetoscopio", "hospital", "paciente", "receta", "bata", "cirugía", "salud", "diagnóstico"
  ❌ INCORRECTO: "ingeniero", "profesor", "chef", "piloto" (son otras profesiones de la misma categoría)

POR QUÉ ESTA REGLA EXISTE:
- Si dices otra palabra de la categoría, estás tratando de adivinar la palabra secreta, lo cual revela que NO la conoces
- Los jugadores que conocen la palabra secreta dan características/cualidades, no otras palabras de la categoría
- El impostor debe imitar este comportamiento: dar características generales de la categoría o inferir características específicas basándose en las pistas de otros

═══════════════════════════════════════════════════════════════════════════════
"""

        role_instructions = {
            "jugador": game_explanation + """
═══════════════════════════════════════════════════════════════════════════════
TU ROL: JUGADOR (conoces la palabra clave secreta)
═══════════════════════════════════════════════════════════════════════════════

ERES UN JUGADOR que conoce la palabra clave secreta. Tu objetivo es decir una palabra relacionada con la palabra clave sin revelarla directamente al impostor.

REGLAS FUNDAMENTALES:
1. NUNCA digas otra palabra de la misma categoría (ej: si la palabra es "fresa" y la categoría es "Frutas", NO digas "manzana")
2. SIEMPRE di una característica, cualidad, uso, sensación o asociación de la palabra clave
3. ⚠️ IMPORTANTE: Puedes y DEBES usar referencias arriesgadas o incluso estiradas para no dar tantas pistas al impostor
4. Encuentra el equilibrio: relacionada pero sutil (no demasiado obvia, no demasiado alejada - pero las referencias estiradas están permitidas y son estratégicas)

ESTRATEGIAS Y EJEMPLOS:

Si la palabra clave es "Fresa" (categoría: Frutas):
  ✅ BUENAS palabras directas: "roja", "pequeña", "dulce", "primavera", "batido", "vitamina", "jugosa", "verano", "semillas"
  ✅ EXCELENTES palabras arriesgadas/estiradas: "valentina", "postre", "helado", "mermelada", "tarta", "decoración", "colorante", "saborizante"
    (Estas son referencias más estiradas pero válidas - "valentina" es un postre de fresa, "colorante" puede referirse al color rojo de la fresa)
  ❌ MALAS palabras: "manzana", "plátano", "naranja" (otras frutas - revelarías que no entiendes el juego)
  ⚠️ Palabras demasiado obvias: "fresa" (la palabra misma), "frutilla" (sinónimo directo)

Si la palabra clave es "Perro" (categoría: Animales):
  ✅ BUENAS palabras directas: "fiel", "ladrar", "paseo", "collar", "amigo", "cola", "huella", "doméstico", "mascota"
  ✅ EXCELENTES palabras arriesgadas/estiradas: "parque", "veterinario", "adopción", "refugio", "premio", "entrenamiento", "exposición", "criador"
    (Estas son referencias más estiradas pero válidas - asociaciones indirectas con perros)
  ❌ MALAS palabras: "gato", "león", "tigre" (otros animales - revelarías que no entiendes el juego)
  ⚠️ Palabras demasiado obvias: "perro" (la palabra misma), "can" (sinónimo directo)

Si la palabra clave es "Fútbol" (categoría: Deportes):
  ✅ BUENAS palabras directas: "balón", "gol", "equipo", "cancha", "portería", "penal", "campeonato", "hincha", "árbitro"
  ✅ EXCELENTES palabras arriesgadas/estiradas: "mundial", "estadio", "entrada", "camiseta", "botines", "táctica", "estrategia", "entrenador", "máster"
    (Estas son referencias más estiradas pero válidas - elementos asociados indirectamente)
  ❌ MALAS palabras: "tenis", "básquetbol", "natación" (otros deportes - revelarías que no entiendes el juego)

CÓMO AJUSTAR TU ESTRATEGIA:

1. Si eres de los PRIMEROS en hablar:
   - Puedes ser un poco más específico (ej: si la palabra es "fresa", puedes decir "roja" o "primavera")
   - Pero evita palabras demasiado obvias que revelen la palabra directamente
   - Considera usar referencias arriesgadas o estiradas desde el inicio para confundir al impostor
   - Ejemplo: Para "fresa" podrías decir "valentina" (postre) o "colorante" (asociación indirecta con el color)

2. Si otros jugadores YA HAN HABLADO:
   - Observa las palabras que dijeron para mantener coherencia
   - Si otros dijeron palabras muy específicas (ej: "batido", "vitamina"), puedes ser más específico también
   - Si otros dijeron palabras genéricas (ej: "dulce", "roja"), mantén un nivel similar
   - Si otros usaron referencias estiradas, tú también puedes usar referencias estiradas
   - Busca patrones: si varios mencionaron características físicas, puedes mencionar otra característica física
   - Si varios mencionaron usos, puedes mencionar otro uso
   - ⚠️ ESTRATEGIA AVANZADA: Si otros dieron pistas muy directas, considera usar una referencia más estirada para balancear y no dar demasiadas pistas al impostor

3. Equilibrio perfecto y referencias arriesgadas:
   - La palabra debe ser lo suficientemente específica para que otros jugadores (que conocen la palabra) entiendan que tú también la conoces
   - Pero no tan específica que el impostor pueda adivinarla fácilmente
   - ⚠️ IMPORTANTE: Usa referencias arriesgadas o incluso estiradas si es necesario para no dar pistas al impostor
   - Las referencias estiradas son válidas y estratégicas: si hay una conexión lógica (aunque sea indirecta), está permitida
   - Ejemplo para "fresa": "batido" es buena porque es específica pero no revela directamente que es fresa (podría ser cualquier fruta en un batido)
   - Ejemplo de referencia estirada para "fresa": "valentina" (postre de fresa) o "colorante" (asociación con el color rojo) - estas son más arriesgadas pero válidas
   - Ejemplo de referencia estirada para "perro": "refugio" o "veterinario" - asociaciones indirectas pero válidas
   - Cuanto más estirada sea la referencia, menos pistas le das al impostor, pero asegúrate de que otros jugadores puedan entender la conexión

Responde SOLO con UNA palabra, sin explicaciones""",
            
            "impostor": game_explanation + """
═══════════════════════════════════════════════════════════════════════════════
TU ROL: IMPOSTOR (solo conoces la CATEGORÍA, NO la palabra clave)
═══════════════════════════════════════════════════════════════════════════════

ERES EL IMPOSTOR. Solo conoces la CATEGORÍA de la palabra, NO la palabra en sí. Tu objetivo es pasar desapercibido actuando como si conocieras la palabra clave.

⚠️ REGLA CRÍTICA PARA EL IMPOSTOR:
- NUNCA digas otra palabra de la misma categoría (ej: si la categoría es "Frutas", NO digas "manzana", "plátano", etc.)
- SIEMPRE di una característica, cualidad, uso, sensación o asociación que podría aplicar a varias palabras de esa categoría
- Actúa como si conocieras la palabra clave: da características que alguien que conoce la palabra daría

ESTRATEGIAS SEGÚN TU POSICIÓN:

═══════════════════════════════════════════════════════════════════════════════
CASO 1: Eres de los PRIMEROS en hablar (pocos o ningún jugador ha hablado)
═══════════════════════════════════════════════════════════════════════════════

Estrategia: Da características GENERALES de la categoría que podrían aplicar a varias palabras.

Ejemplo - Categoría "Frutas":
  ✅ BUENAS palabras: "dulce", "refrescante", "vitamina", "jugosa", "saludable", "natural", "colorida"
  ❌ MALAS palabras: "manzana", "plátano", "naranja" (otras frutas - revelarías que estás adivinando)
  ⚠️ Evita palabras demasiado genéricas como "comida" o "cosa" (sería sospechoso)

Ejemplo - Categoría "Animales":
  ✅ BUENAS palabras: "movimiento", "vida", "naturaleza", "salvaje", "doméstico", "pelaje", "patas"
  ❌ MALAS palabras: "perro", "gato", "león" (otros animales - revelarías que estás adivinando)

Ejemplo - Categoría "Deportes":
  ✅ BUENAS palabras: "competencia", "equipo", "ejercicio", "victoria", "entrenamiento", "cancha"
  ❌ MALAS palabras: "fútbol", "tenis", "básquetbol" (otros deportes - revelarías que estás adivinando)

═══════════════════════════════════════════════════════════════════════════════
CASO 2: Otros jugadores YA HAN HABLADO (tienes pistas para analizar)
═══════════════════════════════════════════════════════════════════════════════

Estrategia: ANALIZA cuidadosamente las palabras de otros jugadores para INFERIR la palabra clave, luego da una característica de esa palabra específica.

PASO 1 - ANALIZA las palabras dichas:
- Busca patrones comunes: ¿mencionan características físicas? ¿usos? ¿sensaciones?
- Intenta inferir la palabra clave basándote en las pistas
- Ejemplo: Si otros dijeron "roja", "pequeña", "primavera" → probablemente es "fresa" o "cereza"
- Ejemplo: Si otros dijeron "fiel", "ladrar", "paseo" → probablemente es "perro"

PASO 2 - Da una característica de la palabra INFERIDA:
- Una vez que infieres la palabra, da una característica específica de esa palabra
- Pero asegúrate de que la característica también podría aplicar a otras palabras similares (por si te equivocaste)
- Ejemplo: Si infieres "fresa" → puedes decir "batido" o "vitamina" (características específicas pero que también podrían aplicar a otras frutas rojas)

EJEMPLOS CONCRETOS:

Escenario 1 - Categoría "Frutas", otros dijeron: "roja", "pequeña", "primavera"
  Tu análisis: Probablemente es "fresa" o "cereza" (frutas rojas pequeñas de primavera)
  ✅ BUENAS palabras: "batido", "vitamina", "jugosa", "dulce", "semillas"
  ❌ MALAS palabras: "manzana", "plátano" (otras frutas - revelarías que estás adivinando)
  ⚠️ Evita palabras demasiado específicas solo de fresa si no estás seguro

Escenario 2 - Categoría "Animales", otros dijeron: "fiel", "ladrar", "paseo"
  Tu análisis: Probablemente es "perro" (animal fiel que ladra y se pasea)
  ✅ BUENAS palabras: "collar", "mascota", "cola", "huella", "doméstico"
  ❌ MALAS palabras: "gato", "león", "tigre" (otros animales - revelarías que estás adivinando)

Escenario 3 - Categoría "Deportes", otros dijeron: "balón", "gol", "equipo"
  Tu análisis: Probablemente es "fútbol" (deporte con balón, goles y equipos)
  ✅ BUENAS palabras: "cancha", "portería", "penal", "campeonato", "hincha"
  ❌ MALAS palabras: "tenis", "básquetbol", "natación" (otros deportes - revelarías que estás adivinando)

AJUSTA TU ESTRATEGIA SEGÚN EL CONTEXTO:

1. Si otros dijeron palabras MUY ESPECÍFICAS:
   - Intenta ser más específico también (basándote en tu inferencia)
   - Ejemplo: Si otros dijeron "batido" y "vitamina" → puedes decir "jugosa" o "semillas"

2. Si otros dijeron palabras GENÉRICAS:
   - Mantén un nivel similar de generalidad
   - Ejemplo: Si otros dijeron "dulce" y "roja" → puedes decir "refrescante" o "natural"

3. Si hay muchas palabras dichas y puedes inferir claramente la palabra:
   - Puedes ser más específico con características de esa palabra
   - Pero siempre características, NUNCA otra palabra de la categoría

4. Si las pistas son contradictorias o confusas:
   - Vuelve a características generales de la categoría
   - Es mejor ser genérico que arriesgarse a decir algo que revele que no conoces la palabra

RECUERDA:
- Actúa como si conocieras la palabra clave sin saberla realmente
- Observa las reacciones implícitas en las palabras de otros jugadores
- Si dices otra palabra de la categoría, inmediatamente revelarás que eres el impostor
- Es mejor ser un poco genérico que arriesgarse a adivinar otra palabra de la categoría

Responde SOLO con UNA palabra, sin explicaciones"""
        }

        self.chain_jugador = dspy.ChainOfThought(
            NPCSignature.with_instructions(role_instructions["jugador"])
        )
        self.chain_impostor = dspy.ChainOfThought(
            NPCSignature.with_instructions(role_instructions["impostor"])
        )

    async def aforward(
        self,
        role: str,
        secret_info: str,
        words_said: str,
        player_names: str,
    ) -> str:
        logger.debug(f"NPC.aforward called with role={role}, secret_info={secret_info}")
        
        if role == "impostor":
            result = await self.chain_impostor.acall(
                role=role,
                secret_info=secret_info,
                words_said=words_said,
                player_names=player_names,
            )
        else:
            result = await self.chain_jugador.acall(
                role=role,
                secret_info=secret_info,
                words_said=words_said,
                player_names=player_names,
            )
        
        word = result.word.strip()
        logger.info(f"NPC generated word: {word}")
        return word


class Vote(Program):
    """Program for AI players to vote on who they think is the impostor."""

    def __init__(self, lm: dspy.LM = None, seed: int = 42):
        super().__init__(lm=lm or get_gpt_5_mini(), seed=seed)

        class VoteSignature(dspy.Signature):
            role: str = dspy.InputField(desc="Tu rol: 'jugador' o 'impostor'")
            secret_info: str = dspy.InputField(desc="Palabra clave si eres jugador, categoria si eres impostor")
            all_words: str = dspy.InputField(desc="Todas las palabras dichas por cada jugador")
            active_players: str = dspy.InputField(desc="Nombres de jugadores que pueden ser votados")
            your_name: str = dspy.InputField(desc="Tu nombre")
            
            reasoning: str = dspy.OutputField(desc="Tu razonamiento sobre quién votar")
            vote: str = dspy.OutputField(desc="Nombre del jugador que votas como impostor")

        role_instructions = {
            "jugador": """Eres un jugador que conoce la palabra clave secreta.
Tu objetivo es identificar al impostor analizando las palabras dichas:
- Busca palabras que sean demasiado genéricas para la categoría
- Busca palabras que no encajen bien con la palabra clave que conoces
- Busca palabras que parezcan aleatorias o fuera de lugar
- Analiza quién dijo qué y compara con la palabra clave que conoces
- NO puedes votarte a ti mismo
- Debes votar por el nombre exacto de uno de los jugadores activos
- Responde SOLO con el nombre del jugador, sin explicaciones""",
            
            "impostor": """Eres el IMPOSTOR. Solo conoces la CATEGORÍA, NO la palabra clave.
Tu objetivo es NO ser descubierto y ganar la ronda:
- Debes votar estratégicamente para no levantar sospechas
- NO votes por ti mismo (sería obvio)
- Analiza las palabras dichas y vota por alguien que parezca sospechoso
- Si dijiste una palabra genérica, NO votes por alguien que también dijo algo genérico (podrían sospechar de ti)
- Intenta votar por alguien que dijo algo que podría parecer fuera de lugar
- Debes votar por el nombre exacto de uno de los jugadores activos
- Responde SOLO con el nombre del jugador, sin explicaciones"""
        }

        self.chain_jugador = dspy.ChainOfThought(
            VoteSignature.with_instructions(role_instructions["jugador"])
        )
        self.chain_impostor = dspy.ChainOfThought(
            VoteSignature.with_instructions(role_instructions["impostor"])
        )

    async def aforward(
        self,
        role: str,
        secret_info: str,
        all_words: str,
        active_players: str,
        your_name: str,
    ) -> str:
        logger.debug(f"Vote.aforward called with role={role}, your_name={your_name}")
        
        if role == "impostor":
            result = await self.chain_impostor.acall(
                role=role,
                secret_info=secret_info,
                all_words=all_words,
                active_players=active_players,
                your_name=your_name,
            )
        else:
            result = await self.chain_jugador.acall(
                role=role,
                secret_info=secret_info,
                all_words=all_words,
                active_players=active_players,
                your_name=your_name,
            )
        
        vote = result.vote.strip()
        logger.info(f"Vote generated vote: {vote}")
        return vote


class GenerateCategoryWord(Program):
    """Program to generate a random category and word for the game."""

    def __init__(self, lm: dspy.LM = None, seed: int = 42):
        super().__init__(lm=lm or get_gpt_5_mini(), seed=seed)

        category_examples = """
Ejemplos de categorías y palabras:

- Frutas: Manzana, Plátano, Naranja, Uva, Fresa, Mango, Piña, Sandía, Melón, Pera
- Animales: Perro, Gato, León, Tigre, Elefante, Jirafa, Oso, Lobo, Zorro, Conejo
- Deportes: Fútbol, Básquetbol, Tenis, Natación, Ciclismo, Atletismo, Boxeo, Voleibol
- Profesiones: Doctor, Ingeniero, Profesor, Chef, Piloto, Bombero, Policía, Arquitecto
- Países: Argentina, México, España, Francia, Italia, Japón, Brasil, Chile, Colombia
- Comidas: Pizza, Hamburguesa, Tacos, Sushi, Pasta, Ensalada, Sopa, Sandwich, Helado
- Colores: Rojo, Azul, Verde, Amarillo, Negro, Blanco, Rosa, Morado, Naranja, Gris
- Transporte: Auto, Avión, Barco, Tren, Bicicleta, Motocicleta, Bus, Subte, Taxi
"""

        class GenerateCategoryWordSignature(dspy.Signature):
            reasoning: str = dspy.OutputField(desc="Tu razonamiento sobre qué categoría y palabra elegir")
            category: str = dspy.OutputField(desc="Una categoría (puede ser una de las ejemplos o una nueva)")
            word: str = dspy.OutputField(desc="Una palabra específica dentro de esa categoría")

        instructions = f"""Genera una categoría y una palabra aleatoria para el juego de impostor.

{category_examples}

Puedes usar una de las categorías de ejemplo o crear una nueva. La palabra debe ser específica y pertenecer claramente a la categoría elegida.

Genera algo variado y creativo, pero asegúrate de que la palabra encaje perfectamente con la categoría."""

        self.chain = dspy.ChainOfThought(
            GenerateCategoryWordSignature.with_instructions(instructions)
        )

    async def aforward(self) -> tuple[str, str]:
        logger.debug("GenerateCategoryWord.aforward called")
        
        result = await self.chain.acall()
        
        category = result.category.strip()
        word = result.word.strip()
        logger.info(f"GenerateCategoryWord generated category: {category}, word: {word}")
        return word, category
