/* Konva-Bühne: logische Tafel 1500 × 1000, auf jedes Gerät passend skaliert. */
(function () {
  const GT = (window.GT = window.GT || {});
  const B = 1500, H = 1000;
  GT.TAFEL = { B, H };

  class Buehne {
    constructor(container) {
      this.container = container;
      this.stage = new Konva.Stage({ container, width: container.clientWidth || 300, height: container.clientHeight || 200 });
      this.hg = new Konva.Layer({ listening: false });
      this.obj = new Konva.Layer({ clip: { x: 0, y: 0, width: B, height: H } });
      this.live = new Konva.Layer({ listening: false });
      this.ui = new Konva.Layer();
      this.stage.add(this.hg, this.obj, this.live, this.ui);
      this.ansicht = { zoom: 1, x: 0, y: 0 };
      this.theme = "kreide";
      this.knoten = new Map();
      this._vorlageUrl = null;
      this.onGroesse = null;
      if (window.ResizeObserver) new ResizeObserver(() => this.anpassen()).observe(container);
      window.addEventListener("resize", () => this.anpassen());
      this.anpassen();
    }

    /** Grundskalierung (Letterbox) + Ansicht (Zoom/Verschiebung) anwenden. */
    anpassen() {
      const w = this.container.clientWidth, h = this.container.clientHeight;
      if (!w || !h) return;
      this.stage.size({ width: w, height: h });
      const s = Math.min(w / B, h / H);
      this.basis = { s, ox: (w - B * s) / 2, oy: (h - H * s) / 2 };
      const z = this.ansicht.zoom || 1;
      this.stage.scale({ x: s * z, y: s * z });
      this.stage.position({ x: this.basis.ox - this.ansicht.x * s * z, y: this.basis.oy - this.ansicht.y * s * z });
      this.stage.batchDraw();
      this.onGroesse && this.onGroesse();
    }

    ansichtSetzen(a) {
      const z = Math.min(4, Math.max(1, a.zoom || 1));
      const x = Math.min(B - B / z, Math.max(0, a.x || 0));
      const y = Math.min(H - H / z, Math.max(0, a.y || 0));
      this.ansicht = { zoom: z, x, y };
      this.anpassen();
    }

    /** Sichtbarer Mittelpunkt in Tafelkoordinaten (für neu eingefügte Objekte). */
    mitte() {
      const z = this.ansicht.zoom;
      return { x: this.ansicht.x + B / z / 2, y: this.ansicht.y + H / z / 2 };
    }

    zuTafel(bildschirm) {
      const t = this.stage.getAbsoluteTransform().copy().invert();
      return t.point(bildschirm);
    }

    zeiger() {
      const p = this.stage.getPointerPosition();
      return p ? this.zuTafel(p) : null;
    }

    zuBildschirm(punkt) {
      return this.stage.getAbsoluteTransform().point(punkt);
    }

    /** Hintergrund zeichnen: Tafelfarbe, Raster, Vorlage. */
    hintergrund(art, vorlageUrl) {
      this.theme = GT.theme(art);
      const t = this.theme;
      this.hg.destroyChildren();
      this.hg.add(new Konva.Rect({ x: -4000, y: -4000, width: B + 8000, height: H + 8000, fill: "#1a1a1a" }));
      this.hg.add(new Konva.Rect({ x: -14, y: -14, width: B + 28, height: H + 28, fill: "#7a5230", cornerRadius: 6 }));
      this.hg.add(new Konva.Rect({ x: 0, y: 0, width: B, height: H, fill: GT.farben.tafel[t] }));
      const linie = (pts, farbe, breite) => this.hg.add(new Konva.Line({ points: pts, stroke: farbe, strokeWidth: breite || 1.5 }));
      const fein = GT.farben.linien[t];
      if (art === "kariert") {
        for (let x = 50; x < B; x += 50) linie([x, 0, x, H], fein);
        for (let y = 50; y < H; y += 50) linie([0, y, B, y], fein);
      } else if (art === "liniert") {
        for (let y = 80; y < H; y += 70) linie([40, y, B - 40, y], fein, 2);
      } else if (art === "koordinaten") {
        for (let x = 150; x < B; x += 50) linie([x, 60, x, H - 60], fein);
        for (let y = 60; y < H - 60; y += 50) linie([150, y, B - 60, y], fein);
        const ax = GT.farben.achsen[t];
        this.hg.add(new Konva.Arrow({ points: [150, H - 110, B - 50, H - 110], stroke: ax, fill: ax, strokeWidth: 3, pointerLength: 16, pointerWidth: 14 }));
        this.hg.add(new Konva.Arrow({ points: [200, H - 60, 200, 40], stroke: ax, fill: ax, strokeWidth: 3, pointerLength: 16, pointerWidth: 14 }));
      }
      this._vorlageUrl = vorlageUrl || null;
      if (vorlageUrl) {
        GT.ladeBild(vorlageUrl).then((img) => {
          if (this._vorlageUrl !== vorlageUrl) return;
          const s = Math.min((B - 40) / img.width, (H - 40) / img.height);
          this.hg.add(new Konva.Image({ image: img, x: (B - img.width * s) / 2, y: (H - img.height * s) / 2,
            width: img.width * s, height: img.height * s }));
          this.hg.batchDraw();
        }).catch(() => {});
      }
      this.hg.batchDraw();
    }

    /** Alle Objekte einer Seite neu aufbauen. */
    seiteZeigen(seite) {
      this.obj.destroyChildren();
      this.knoten.clear();
      this.hintergrund(seite.hintergrund, seite.vorlage_url);
      for (const o of seite.objekte) this.objektEinfuegen(o);
      this.obj.batchDraw();
    }

    objektEinfuegen(o, index) {
      if (this.knoten.has(o.id)) this.objektEntfernen(o.id);
      const g = GT.darstellung.erzeuge(o, this.theme);
      this.obj.add(g);
      if (typeof index === "number" && index < this.obj.children.length - 1) g.zIndex(index);
      if (o.typ === "strich" && o.marker) g.moveToBottom(); // Textmarker liegt unter Schrift und Formeln
      this.knoten.set(o.id, g);
      this.obj.batchDraw();
      return g;
    }

    objektAendern(id, aenderungen) {
      const g = this.knoten.get(id);
      if (!g) return;
      const o = Object.assign({}, g.getAttr("daten"), aenderungen);
      const nurGeometrie = Object.keys(aenderungen).every((k) => ["x", "y", "rotation", "skala"].includes(k));
      if (nurGeometrie) {
        g.setAttr("daten", o);
        GT.darstellung.geometrie(g, o);
      } else {
        const z = g.zIndex();
        this.objektEinfuegen(o, z);
      }
      this.obj.batchDraw();
    }

    /** Objekt mit unverändertem Inhalt neu zeichnen (z. B. geänderte Feldsperren). */
    neuZeichnen(id) {
      const g = this.knoten.get(id);
      if (g) this.objektEinfuegen(g.getAttr("daten"), g.zIndex());
    }

    objektEntfernen(id) {
      const g = this.knoten.get(id);
      if (g) { g.destroy(); this.knoten.delete(id); this.obj.batchDraw(); }
    }

    /** Objekt-Gruppe zu einem getroffenen Konva-Knoten finden. */
    gruppeVon(knoten) {
      while (knoten && knoten !== this.obj) {
        if (knoten.name && knoten.name() === "obj") return knoten;
        knoten = knoten.getParent();
      }
      return null;
    }

    /** Eine Seite unabhängig von der aktuellen Ansicht als PNG rendern. */
    static async exportieren(seite, pixelRatio, mimeType, quality) {
      const div = document.createElement("div");
      div.style.cssText = "position:fixed;left:-99999px;top:0;width:1500px;height:1000px;";
      document.body.appendChild(div);
      const b = new Buehne(div);
      b.stage.scale({ x: 1, y: 1 });
      b.stage.position({ x: 0, y: 0 });
      b.stage.size({ width: B, height: H });
      b.anpassen = () => {};
      b.seiteZeigen(seite);
      await new Promise((ok) => setTimeout(ok, 900)); // Bilder und Formeln laden lassen
      const url = b.stage.toDataURL({ x: 0, y: 0, width: B, height: H, pixelRatio: pixelRatio || 1.2,
        mimeType: mimeType || "image/png", quality: quality || 0.85 });
      b.stage.destroy();
      div.remove();
      return url;
    }
  }

  GT.Buehne = Buehne;
})();
