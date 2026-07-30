import networkx as nx
from pyvis.network import Network

# ==========================================
# 1. INICIALIZACIÓN DEL GRAFO
# ==========================================
G = nx.Graph()

# ==========================================
# 2. DEFINICIÓN DE IDs CONCEPTUALES Y NODOS CENTRALES
# ==========================================
# Al usar los nombres como ID, el select_menu mostrará textos limpios y temáticos.
c_id = "Sistema: Desigualdad Socioespacial"
v1_id = "Vértice I: Financiarización y Precio"
v2_id = "Vértice II: Urbanismo Neoliberal"
v3_id = "Vértice III: Hábitat Precario y Cuidados"

G.add_node(c_id, label="DESIGUALDAD SOCIOESPACIAL\nCOMO SISTEMA", size=25, 
           color="#000000", font={"color": "black", "size": 22, "face": "Helvetica", "bold": True})

G.add_node(v1_id, label="Vértice I: Espacio Concebido\n(Financiarización)", size=15, 
           color="#333333", font={"color": "black", "size": 16, "face": "Helvetica", "bold": True})
G.add_node(v2_id, label="Vértice II: Espacio Percibido\n(Urbanismo Neoliberal)", size=15, 
           color="#333333", font={"color": "black", "size": 16, "face": "Helvetica", "bold": True})
G.add_node(v3_id, label="Vértice III: Espacio Vivido\n(Hábitat Precario)", size=15, 
           color="#333333", font={"color": "black", "size": 16, "face": "Helvetica", "bold": True})

# Configuración de colores con transparencia (RGBA)
color_arista_principal = "rgba(136, 136, 136, 0.4)"  # Líneas estructurales (centro a vértices)
color_arista_paper = "rgba(210, 210, 210, 0.6)"      # Líneas de pertenencia (vértice a paper)
color_arista_afinidad = "rgba(150, 150, 150, 0.4)"   # Líneas de constelación (paper a paper)

# Conexiones estructurales
G.add_edge(c_id, v1_id, value=8, color=color_arista_principal)
G.add_edge(c_id, v2_id, value=8, color=color_arista_principal)
G.add_edge(c_id, v3_id, value=8, color=color_arista_principal)

# ==========================================
# 3. DATOS DEL CORPUS CON IDs TEMÁTICOS
# ==========================================
nodo_paper_args = {"size": 8, "color": "#000000", "font": {"color": "#000000", "size": 11, "face": "Helvetica"}}

# Formato: ("ID Temático que saldrá en el menú", "Etiqueta visible en el nodo con saltos de línea")
papers_v1 = [
    ("Precios y financierización (INVI, 2021)", "Precios y financierización\n(INVI, 2021)"), 
    ("Is there financialisation? (Economies, 2022)", "Is there financialisation...\n(Economies, 2022)"),
    ("Plusvalía urbana (ACE, 2020)", "Plusvalía urbana\n(ACE, 2020)"), 
    ("Subsidios habitacionales (ACE, 2023)", "Subsidios habitacionales\n(ACE, 2023)"),
    ("Hedonic prices (CHA, 2023)", "Hedonic prices\n(CHA, 2023)"), 
    ("Determinantes urbanos (Urbano, 2021)", "Determinantes urbanos\n(Urbano, 2021)"),
    ("Financialized housing: Verticalization (CEA, 2021)", "Financialized housing:\nVerticalization (CEA, 2021)"), 
    ("Unregulated markets (Buildings, 2019)", "Unregulated markets\n(Buildings, 2019)"),
    ("Central bank influence (2026)", "Central bank influence\n(2026)"), 
    ("Inflation & construction (RIC, 2024)", "Inflation & construction\n(2024)"),
    ("Exploring the contradiction (JPER, 2024)", "Exploring the contradiction\n(JPER, 2024)"), 
    ("Inversionistificación en AL (2019)", "Inversionistificación en AL\n(2019)"),
    ("Investification (Ciudades, 2022)", "Investification\n(Ciudades, 2022)"), 
    ("Investification (Urbano, 2024)", "Investification\n(Urbano, 2024)"),
    ("The 15-minute city and real estate (2025)", "15-minute city\n(2025)"), 
    ("Financial agency in neoliberal design (2023)", "Financial agency in design\n(2023)"),
    ("Dimensions of surplus value (s.f.)", "Dimensions of surplus value\n(s.f.)")
]

papers_v2 = [
    ("Big bang of neoliberal urbanism (2019)", "Big bang of neoliberal\nurbanism (2019)"), 
    ("Implosión-explosión de Lefebvre (2017)", "Implosión-explosión\nLefebvre (2017)"),
    ("Bread for right to the city (2019)", "Right to the city\n(2019)"), 
    ("Vida urbana neoliberal (2019)", "Vida urbana neoliberal\n(2019)"),
    ("Contradiction in ethos of practitioners (2020)", "Contradiction in ethos\n(2020)"), 
    ("Pinochet's repressive urbanism (2021)", "Pinochet's repressive\nurbanism (2021)"),
    ("Reimaginando el marxismo (2016)", "Reimaginando el marxismo\n(2016)"), 
    ("Actos de disenso (2019)", "Actos de disenso\n(2019)"),
    ("Half happy architecture (2018)", "Half happy architecture\n(2018)"), 
    ("Neoliberalism and urban development (2017)", "Neoliberalism & urban dev.\n(2017)"),
    ("Neoliberalandia (2018)", "Neoliberalandia\n(2018)"), 
    ("Espacios constitucionales (2022)", "Espacios constitucionales\n(2022)"),
    ("Political economy of housing (2023)", "Political economy of housing\n(2023)"), 
    ("Commodification of urban planners (2023)", "Commodification of planners\n(2023)"),
    ("AI-driven deconstruction of regulations (s.f.)", "AI-driven deconstruction\n(s.f.)"), 
    ("Can public housing be innovative? (s.f.)", "Innovative public housing\n(s.f.)"),
    ("Contesting sustainable cities (s.f.)", "Sustainable cities\n(s.f.)"), 
    ("Urban society in tension (2023)", "Urban society in tension\n(2023)"),
    ("The vertical ghetto (2025)", "The vertical ghetto\n(2025)"), 
    ("Determinants of urban sprawl (2021)", "Urban sprawl in LA\n(2021)")
]

papers_v3 = [
    ("Precios, auge y campamentos (2019)", "Precios, auge y\ncampamentos (2019)"), 
    ("COVID-19 and housing conditions (2020)", "COVID-19 and housing\n(2020)"),
    ("Socioeconomic drivers of slums (2022)", "Socioeconomic drivers\nof slums (2022)"), 
    ("Vivienda informal (2023)", "Vivienda informal\n(2023)"),
    ("Los Arenales (2023)", "Los Arenales\n(2023)"), 
    ("Los Arenales: derecho a la ciudad (2024)", "Arenales: derecho\na la ciudad (2024)"),
    ("Geographical research and PPGIS (2020)", "Geographical research PPGIS\n(2020)"), 
    ("Co-producing the right to fail (2020)", "Co-producing the right\nto fail (2020)"),
    ("Food insecurity and overcrowding (s.f.)", "Food insecurity &\novercrowding (s.f.)"), 
    ("Unveiling place-based effects (s.f.)", "Unveiling place-based\neffects (s.f.)"),
    ("Ollas comunes (s.f.)", "Ollas comunes\n(s.f.)"), 
    ("A caring smart city (2026)", "Caring smart city\n(2026)"),
    ("Smart cities y cuidados (2023)", "Smart cities y cuidados\n(2023)"), 
    ("Dónde estudian los más pequeños (s.f.)", "Dónde estudian los pequeños\n(s.f.)"),
    ("Greening extractivisms (s.f.)", "Extractivism & Greening\n(s.f.)"), 
    ("Housing affordability in the US (s.f.)", "Housing affordability US\n(s.f.)")
]

# Agregar nodos y conectarlos a su vértice
for p_id, p_label in papers_v1:
    G.add_node(p_id, label=p_label, **nodo_paper_args)
    G.add_edge(v1_id, p_id, value=1, color=color_arista_paper)

for p_id, p_label in papers_v2:
    G.add_node(p_id, label=p_label, **nodo_paper_args)
    G.add_edge(v2_id, p_id, value=1, color=color_arista_paper)

for p_id, p_label in papers_v3:
    G.add_node(p_id, label=p_label, **nodo_paper_args)
    G.add_edge(v3_id, p_id, value=1, color=color_arista_paper)

# ==========================================
# 4. AFINIDADES TEMÁTICAS TRANSVERSALES (Líneas transparentes)
# ==========================================
# Al usar los IDs reales (títulos), las conexiones quedan explícitas en el código
afinidades = [
    ("Precios y financierización (INVI, 2021)", "Precios, auge y campamentos (2019)", 4),
    ("Financialized housing: Verticalization (CEA, 2021)", "The vertical ghetto (2025)", 5),
    ("Exploring the contradiction (JPER, 2024)", "Contradiction in ethos of practitioners (2020)", 4),
    ("Financial agency in neoliberal design (2023)", "Commodification of urban planners (2023)", 3),
    ("Bread for right to the city (2019)", "Los Arenales: derecho a la ciudad (2024)", 4),
    ("Political economy of housing (2023)", "Dimensions of surplus value (s.f.)", 5),
    ("Contesting sustainable cities (s.f.)", "Greening extractivisms (s.f.)", 3),
    ("A caring smart city (2026)", "Smart cities y cuidados (2023)", 4),
    ("Inversionistificación en AL (2019)", "Investification (Ciudades, 2022)", 5),
    ("Investification (Ciudades, 2022)", "Investification (Urbano, 2024)", 5),
    ("Co-producing the right to fail (2020)", "Big bang of neoliberal urbanism (2019)", 2)
]

for origen, destino, grosor in afinidades:
    G.add_edge(origen, destino, value=grosor, color=color_arista_afinidad)

# ==========================================
# 5. CONFIGURACIÓN Y EXPORTACIÓN PYVIS
# ==========================================
net = Network(height="900px", width="100%", bgcolor="#ffffff", font_color="#000000", select_menu=True)

net.from_nx(G)

# Física de constelación ajustada
net.force_atlas_2based(
    gravity=-60,
    central_gravity=0.015,
    spring_length=150,
    spring_strength=0.05,
    damping=0.6,
    overlap=0.5
)

net.show_buttons(filter_=['physics'])
archivo_salida = "constelacion_lefebvriana.html"
net.write_html(archivo_salida)
print(f"Gráfico generado con éxito. Abre '{archivo_salida}'.")

import matplotlib.pyplot as plt

# 1. Definir la distribución espacial de los nodos (layout)
# spring_layout simula la gravedad y repulsión, similar a ForceAtlas
posiciones = nx.spring_layout(G, k=0.6, iterations=100)

# 2. Crear una figura en blanco de alta resolución (tamaño en pulgadas)
plt.figure(figsize=(16, 12))

# 3. Dibujar los elementos por separado para que Illustrator los lea bien
# Nodos
nx.draw_networkx_nodes(G, posiciones, node_size=80, node_color="black")

# Aristas (líneas) - extraemos opacidad y color gris
nx.draw_networkx_edges(G, posiciones, alpha=0.3, edge_color="#888888", width=1.5)

# Textos
nx.draw_networkx_labels(G, posiciones, font_size=8, font_family="Helvetica", font_color="black")

# 4. Limpiar los ejes del gráfico por defecto de matplotlib
plt.axis("off")

# 5. Exportar el archivo como SVG vectorial
archivo_svg = "constelacion_lefebvriana.svg"
plt.savefig(archivo_svg, format="svg", bbox_inches="tight", transparent=True)

print(f"✅ Archivo vectorial guardado como '{archivo_svg}'. Listo para abrir en Illustrator.")
