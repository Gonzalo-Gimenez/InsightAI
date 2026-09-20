"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import type { MetricsResponse } from "@/lib/api";

interface Chart3dProps {
  metrics: MetricsResponse;
}

function paleta(index: number, total: number): number {
  const hue = (index / Math.max(total, 1)) * 300;
  return new THREE.Color().setHSL(hue / 360, 0.75, 0.55).getHex();
}

function makeLabel(text: string, x: number, height: number): THREE.Sprite {
  const canvas = document.createElement("canvas");
  canvas.width = 256;
  canvas.height = 128;
  const ctx = canvas.getContext("2d");
  if (ctx) {
    ctx.font = "bold 30px Arial";
    ctx.fillStyle = "#e6ecff";
    ctx.textAlign = "center";
    ctx.fillText(text, 128, 58);
  }
  const texture = new THREE.CanvasTexture(canvas);
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: texture }));
  sprite.position.set(x, height + 0.5, 0);
  sprite.scale.set(2.6, 1.2, 1);
  return sprite;
}

function buildBars(scene: THREE.Scene, metrics: MetricsResponse, labels: THREE.Sprite[]) {
  const entries = Object.entries(metrics.ventas_por_categoria).sort(
    (a, b) => b[1] - a[1],
  );
  const max = Math.max(...entries.map(([, value]) => value));
  const count = entries.length;
  const spacing = 2.4;
  const offset = ((count - 1) * spacing) / 2;

  entries.forEach(([categoria, valor], index) => {
    const height = (valor / max) * 5;
    const color = paleta(index, count);
    const material = new THREE.MeshStandardMaterial({
      color,
      emissive: new THREE.Color(color).multiplyScalar(0.25),
    });
    const geometry = new THREE.BoxGeometry(1.6, height, 1.6);
    const bar = new THREE.Mesh(geometry, material);
    bar.position.x = index * spacing - offset;
    bar.position.y = height / 2;

    const label = makeLabel(`${categoria} · $${valor}`, index * spacing - offset, height);
    scene.add(bar, label);
    labels.push(label);
  });
}

function clearBars(scene: THREE.Scene, labels: THREE.Sprite[]) {
  scene.children
    .filter((child) => child instanceof THREE.Mesh || child instanceof THREE.Sprite)
    .forEach((child) => scene.remove(child));
  labels.forEach((label) => label.material.dispose());
  labels.length = 0;
}

export function Chart3d({ metrics }: Chart3dProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) {
      return;
    }

    const labels: THREE.Sprite[] = [];
    const width = container.clientWidth || 600;
    const height = container.clientHeight || 400;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0b1020);

    const camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
    camera.position.set(0, 6, 14);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.shadowMap.enabled = true;
    container.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;

    const ambient = new THREE.AmbientLight(0xffffff, 0.5);
    const directional = new THREE.DirectionalLight(0xffffff, 1.2);
    directional.position.set(6, 10, 8);
    scene.add(ambient, directional);
    scene.add(new THREE.GridHelper(20, 20, 0x3355aa, 0x223366));

    buildBars(scene, metrics, labels);

    let frameId = 0;
    const animate = () => {
      frameId = requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    const onResize = () => {
      const w = container.clientWidth || 600;
      const h = container.clientHeight || 400;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };

    const observer = new ResizeObserver(onResize);
    observer.observe(container);

    return () => {
      cancelAnimationFrame(frameId);
      observer.disconnect();
      clearBars(scene, labels);
      renderer.dispose();
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
    };
  }, [metrics]);

  return (
    <div
      ref={containerRef}
      className="h-full min-h-[320px] w-full"
    />
  );
}
