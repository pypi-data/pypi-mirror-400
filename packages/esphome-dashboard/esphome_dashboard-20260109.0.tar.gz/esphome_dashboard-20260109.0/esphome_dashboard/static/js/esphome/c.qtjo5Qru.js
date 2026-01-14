import{D as o,_ as t,e as i,n as e,s,x as n,G as a,o as l}from"./index-BmiryCYx.js";import"./c.C2tMW8Lk.js";import"./c.BGvDvYXq.js";let c=class extends s{render(){return n`
      <esphome-process-dialog
        .heading=${`Clean ${this.configuration}`}
        .type=${this.type}
        .spawnParams=${{configuration:this.configuration}}
        @closed=${this._handleClose}
      >
        <mwc-button
          slot="secondaryAction"
          dialogAction="close"
          label="Edit"
          @click=${this._openEdit}
        ></mwc-button>
        <mwc-button
          slot="secondaryAction"
          dialogAction="close"
          label="Install"
          @click=${this._openInstall}
        ></mwc-button>
      </esphome-process-dialog>
    `}_openEdit(){a(this.configuration)}_openInstall(){l(this.configuration)}_handleClose(){this.parentNode.removeChild(this)}};c.styles=[o],t([i()],c.prototype,"configuration",void 0),t([i()],c.prototype,"type",void 0),c=t([e("esphome-clean-dialog")],c);
//# sourceMappingURL=c.qtjo5Qru.js.map
