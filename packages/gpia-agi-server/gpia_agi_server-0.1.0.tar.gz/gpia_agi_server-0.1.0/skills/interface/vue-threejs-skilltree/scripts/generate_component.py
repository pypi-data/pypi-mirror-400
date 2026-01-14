import argparse
import json
from pathlib import Path


def ascii_only(text: str) -> str:
    return text.encode("ascii", "ignore").decode("ascii")


def clamp(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)].rstrip() + "..."


def load_nodes(index_path: Path):
    data = json.loads(index_path.read_text(encoding="utf-8"))
    nodes = []
    for skill in data.get("skills", []):
        name = ascii_only(skill.get("name", ""))
        desc = ascii_only(skill.get("description", ""))
        nodes.append(
            {
                "id": skill.get("id", name),
                "name": name,
                "description": clamp(desc, 120),
            }
        )
    return nodes


def build_component(nodes, title: str) -> str:
    nodes_json = json.dumps(nodes, indent=2, ensure_ascii=True)
    return f"""<template>
  <div ref=\"mount\" class=\"skilltree\"></div>
  <div class=\"legend\" v-if=\"hoverLabel\">{{{{ hoverLabel }}}}</div>
</template>

<script setup>
import {{ onMounted, onBeforeUnmount, ref }} from 'vue'
import * as THREE from 'three'
import {{ OrbitControls }} from 'three/examples/jsm/controls/OrbitControls.js'

const mount = ref(null)
const hoverLabel = ref('')

const rawNodes = {nodes_json}

const scene = new THREE.Scene()
const camera = new THREE.PerspectiveCamera(60, 1, 0.1, 1000)
const renderer = new THREE.WebGLRenderer({{ antialias: true }})
const raycaster = new THREE.Raycaster()
const mouse = new THREE.Vector2()

let animationId = null
let controls = null
const meshes = []

function buildLayout() {{
  const total = rawNodes.length || 1
  const layers = 4
  const radius = 24
  const spread = 12

  return rawNodes.map((node, i) => {{
    const angle = (i / total) * Math.PI * 2
    const layer = i % layers
    const layerRadius = radius + layer * 2
    const y = ((layer / (layers - 1)) - 0.5) * spread
    return {{
      ...node,
      x: Math.cos(angle) * layerRadius,
      y,
      z: Math.sin(angle) * layerRadius,
    }}
  }})
}}

function buildScene() {{
  scene.background = new THREE.Color('#0b0f14')
  camera.position.set(0, 0, 55)

  const layout = buildLayout()
  const nodeGeometry = new THREE.SphereGeometry(0.45, 16, 16)

  layout.forEach((node) => {{
    const material = new THREE.MeshBasicMaterial({{ color: '#8bb4ff' }})
    const mesh = new THREE.Mesh(nodeGeometry, material)
    mesh.position.set(node.x, node.y, node.z)
    mesh.userData = node
    scene.add(mesh)
    meshes.push(mesh)
  }})

  const coreMaterial = new THREE.MeshBasicMaterial({{ color: '#f9d66b' }})
  const core = new THREE.Mesh(new THREE.SphereGeometry(0.9, 20, 20), coreMaterial)
  core.position.set(0, 0, 0)
  core.userData = {{ name: 'GPIA Core', description: 'Central orchestrator for skill execution.' }}
  scene.add(core)
  meshes.push(core)

  const linkMaterial = new THREE.LineBasicMaterial({{ color: '#2f3b4a' }})
  const linkGeometry = new THREE.BufferGeometry()
  const positions = []
  layout.forEach((node) => {{
    positions.push(0, 0, 0, node.x, node.y, node.z)
  }})
  linkGeometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3))
  const lines = new THREE.LineSegments(linkGeometry, linkMaterial)
  scene.add(lines)
}}

function onResize() {{
  if (!mount.value) return
  const {{ clientWidth, clientHeight }} = mount.value
  camera.aspect = clientWidth / clientHeight
  camera.updateProjectionMatrix()
  renderer.setSize(clientWidth, clientHeight)
}}

function onPointerMove(event) {{
  if (!mount.value) return
  const rect = mount.value.getBoundingClientRect()
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1

  raycaster.setFromCamera(mouse, camera)
  const hits = raycaster.intersectObjects(meshes)
  if (hits.length > 0) {{
    const data = hits[0].object.userData || {{}}
    const name = data.name || ''
    const desc = data.description || ''
    hoverLabel.value = desc ? `${{name}}: ${{desc}}` : name
  }} else {{
    hoverLabel.value = ''
  }}
}}

function animate() {{
  animationId = requestAnimationFrame(animate)
  if (controls) controls.update()
  renderer.render(scene, camera)
}}

onMounted(() => {{
  if (!mount.value) return
  renderer.setPixelRatio(window.devicePixelRatio || 1)
  mount.value.appendChild(renderer.domElement)
  buildScene()
  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  onResize()
  window.addEventListener('resize', onResize)
  renderer.domElement.addEventListener('pointermove', onPointerMove)
  animate()
}})

onBeforeUnmount(() => {{
  window.removeEventListener('resize', onResize)
  if (renderer && renderer.domElement) {{
    renderer.domElement.removeEventListener('pointermove', onPointerMove)
  }}
  if (animationId) cancelAnimationFrame(animationId)
  if (renderer) renderer.dispose()
}})
</script>

<style scoped>
.skilltree {{
  width: 100%;
  height: 100vh;
}}

.legend {{
  position: fixed;
  left: 20px;
  bottom: 20px;
  max-width: 420px;
  background: rgba(11, 15, 20, 0.8);
  color: #e7eef8;
  border: 1px solid #2f3b4a;
  padding: 12px 14px;
  border-radius: 10px;
  font-family: 'Iosevka', 'Consolas', 'Courier New', monospace;
  font-size: 12px;
}}
</style>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a Vue 3 + Three.js skilltree component")
    parser.add_argument("--index", default="skills/INDEX.json")
    parser.add_argument("--output", default="runs/SkillTree3D.vue")
    parser.add_argument("--title", default="SkillTree3D")
    args = parser.parse_args()

    index_path = Path(args.index)
    output_path = Path(args.output)

    nodes = load_nodes(index_path)
    component = build_component(nodes, args.title)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(component, encoding="utf-8")
    print(f"wrote {output_path} with {len(nodes)} nodes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
