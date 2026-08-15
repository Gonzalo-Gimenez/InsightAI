import { Component, Input, OnDestroy, OnChanges, AfterViewInit, ElementRef, ViewChild, SimpleChanges } from '@angular/core';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import type { MetricsResponse } from '../../services/api.service';

@Component({
  selector: 'app-chart3d',
  standalone: true,
  template: `<div #container class="chart-container"></div>`,
  styles: [
    `
      :host {
        display: block;
        width: 100%;
        height: 100%;
      }
      .chart-container {
        width: 100%;
        height: 100%;
      }
    `,
  ],
})
export class Chart3dComponent implements AfterViewInit, OnDestroy, OnChanges {
  @ViewChild('container') container!: ElementRef<HTMLDivElement>;
  @Input() metrics: MetricsResponse | null = null;

  private renderer!: THREE.WebGLRenderer;
  private scene!: THREE.Scene;
  private camera!: THREE.PerspectiveCamera;
  private controls!: OrbitControls;
  private labels: THREE.Sprite[] = [];
  private frameId = 0;

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['metrics'] && this.scene && this.metrics) {
      this.clearBars();
      this.buildBars(this.metrics);
    }
  }

  ngAfterViewInit(): void {
    this.initScene();
    if (this.metrics) {
      this.buildBars(this.metrics);
    }
    this.animate();
  }

  ngOnDestroy(): void {
    cancelAnimationFrame(this.frameId);
    this.clearBars();
    this.renderer?.dispose();
  }

  private clearBars(): void {
    this.scene?.children
      .filter((child) => child instanceof THREE.Mesh || child instanceof THREE.Sprite)
      .forEach((child) => this.scene.remove(child));
    this.labels.forEach((label) => label.material.dispose());
    this.labels = [];
  }

  private initScene(): void {
    const width = this.container.nativeElement.clientWidth || 600;
    const height = this.container.nativeElement.clientHeight || 400;

    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x0b1020);

    this.camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
    this.camera.position.set(0, 6, 14);
    this.camera.lookAt(0, 0, 0);

    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(width, height);
    this.renderer.shadowMap.enabled = true;
    this.container.nativeElement.appendChild(this.renderer.domElement);

    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;

    const ambient = new THREE.AmbientLight(0xffffff, 0.5);
    const directional = new THREE.DirectionalLight(0xffffff, 1.2);
    directional.position.set(6, 10, 8);
    this.scene.add(ambient, directional);

    this.scene.add(new THREE.GridHelper(20, 20, 0x3355aa, 0x223366));
  }

  private buildBars(metrics: MetricsResponse): void {
    const entries = Object.entries(metrics.ventas_por_categoria).sort((a, b) => b[1] - a[1]);
    const max = Math.max(...entries.map(([, value]) => value));
    const count = entries.length;
    const spacing = 2.4;
    const offset = ((count - 1) * spacing) / 2;

    const material = new THREE.MeshStandardMaterial({ color: 0x4f8cff, emissive: 0x102850 });

    entries.forEach(([categoria, valor], index) => {
      const height = (valor / max) * 5;
      const geometry = new THREE.BoxGeometry(1.6, height, 1.6);
      const bar = new THREE.Mesh(geometry, material);
      bar.position.x = index * spacing - offset;
      bar.position.y = height / 2;

      const label = this.makeLabel(categoria, index * spacing - offset, height);
      this.scene.add(bar, label);
      this.labels.push(label);
    });
  }

  private makeLabel(text: string, x: number, height: number): THREE.Sprite {
    const canvas = document.createElement('canvas');
    canvas.width = 256;
    canvas.height = 128;
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.font = 'bold 32px Arial';
      ctx.fillStyle = '#cfd8ff';
      ctx.textAlign = 'center';
      ctx.fillText(text, 128, 60);
    }
    const texture = new THREE.CanvasTexture(canvas);
    const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: texture }));
    sprite.position.set(x, height + 0.5, 0);
    sprite.scale.set(2, 1, 1);
    return sprite;
  }

  private animate(): void {
    this.frameId = requestAnimationFrame(() => this.animate());
    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }
}