import { Signal } from '@lumino/signaling';
import { Widget } from '@lumino/widgets';
import { KernelSpecItem, KernelStatus } from './Common';
import { JupyterFrontEnd } from '@jupyterlab/application';

export class KernelList extends Widget {

  private _app: JupyterFrontEnd;

  readonly addNewRequested = new Signal<this, void>(this);
  readonly addExistingRequested = new Signal<this, void>(this);
  readonly connectRequested = new Signal<this, KernelSpecItem>(this);
  readonly disconnectRequested = new Signal<this, KernelSpecItem>(this);
  private _busy: Map<string, boolean> = new Map();

  private _kernels: KernelSpecItem[] = [
    {
      id: 'nexus-dev-mode',
      name: 'Nexus Dev mode',
      status: 'available',
      metadata: ['Lightweight kernel for low-performance and exploratory tasks.'],
      url: 'http://localhost:8080',
      token: ''
    },
    {
      id: 'kernel-5',
      name: 'Kernel 5',
      status: 'available',
      metadata: ['Nodes - 1 | Cores - 39 | Memory-100GB', 'Cluster 1'],
      url: 'http://localhost:8080',
      token: ''
    },    
  ];

  constructor(app: JupyterFrontEnd) {
    super();
    this._app = app;
    this.id = 'cybershuttle-kernel-list';
    this.addClass('csKernelPanel');

    (this._app.serviceManager.kernelspecs as any).refreshSpecs();
    console.log('CyberShuttlePanel initialized with kernelspecs ' );
    console.log(this._app.serviceManager.kernelspecs.specs);

    const kernelspecs = this._app.serviceManager.kernelspecs.specs;
    for (const key of Object.keys(kernelspecs?.kernelspecs || {})) {
      console.log(` - ${key}: `, kernelspecs?.kernelspecs[key]);  
      const spec = kernelspecs?.kernelspecs[key];
      // Safely access kernel_provisioner: ensure it's an object before indexing
      const provisioner = spec?.metadata?.kernel_provisioner;
      if (provisioner && typeof provisioner === 'object' && !Array.isArray(provisioner)) {
        const provName = (provisioner as Record<string, any>)['provisioner_name'];
        if (provName === "cspyk-provisioner") {
          // Add logic here if needed
          console.log(` --> Found CyberShuttle provisioner for kernel spec: ${key}`);

          const kernel = this._kernels.find(k => k.id === key);
          if (kernel) {
            this.updateKernelSpecStatus(key, 'connected');
          } else {
            this.addKernelSpecItem({ 
              id: key, name: key, 
              status: 'connected', metadata: [''], 
              url: 'sfsdf', token: 'dsffs' });
          }
        }
      }
    }

    this._render();
  }

  setBusy(name: string, busy: boolean): void {
    if (busy) this._busy.set(name, true);
    else this._busy.delete(name);
    this._render();
  }


  addKernelSpecItem(kernelSpecItem: KernelSpecItem): void {
    this._kernels.unshift(kernelSpecItem);
    this._render();
  }

  updateKernelSpecStatus(id: string, status: KernelStatus): void {
    const k = this._kernels.find(k => k.id === id);
    if (k) {
      k.status = status;
      this._render();
    }
  }

  private _render(): void {
    this.node.textContent = '';
    this.node.appendChild(this._build());
  }

  private onKernelConnectClicked(id: string): void {
    console.log('[KernelList] connect clicked for', id);
    const kernel = this._kernels.find(k => k.id === id);
    if (!kernel) {
      console.warn('[KernelList] could not find kernel to connect:', id);
      return;
    }
    // emit a signal so the host panel can start/connect the kernel session
    this.connectRequested.emit(kernel);
  }

  private _build(): HTMLElement {
    const root = document.createElement('div');
    root.className = 'csRoot';

    // header
    root.appendChild(this._topBar());
    root.appendChild(this._intro());

    // section header with "+ Add new"
    const sectionHeader = document.createElement('div');
    sectionHeader.className = 'csSectionHeader';
    sectionHeader.appendChild(this._el('div', 'KERNELS'));

    const addBtn = document.createElement('button');
    addBtn.className = 'csAddNew';
    addBtn.type = 'button';
    addBtn.textContent = '+ Add new';
  addBtn.onclick = () => this.addNewRequested.emit(undefined);
    sectionHeader.appendChild(addBtn);
    
  const addExistingBtn = document.createElement('button');
  addExistingBtn.className = 'csAddExisting';
  addExistingBtn.type = 'button';
  addExistingBtn.textContent = '+ Add existing';
  addExistingBtn.onclick = () => this.addExistingRequested.emit(undefined);
  sectionHeader.appendChild(addExistingBtn);
    root.appendChild(sectionHeader);

    // Connected
    root.appendChild(this._subhead(`Connected Kernel Specs (${this._kernels.filter(k => k.status === 'connected').length})`));
    root.appendChild(
      this._card(
        this._kernels
          .filter(k => k.status === 'connected')
          .map(k => this._row(k.name, 'Disconnect', () => this.disconnectRequested.emit(k)))
      )
    );

    // Available
    root.appendChild(this._subhead(`Available Kernel Specs (${this._kernels.filter(k => k.status === 'available').length})`));
    root.appendChild(
      this._card(
        this._kernels
          .filter(k => k.status === 'available')
          .map(k => this._kernelBlock(k, 'Connect', () => this.onKernelConnectClicked(k.id), true))
      )
    );


    // Pending/Rejected
    const pr = this._kernels.filter(k => k.status === 'pending' || k.status === 'rejected');
    root.appendChild(this._subhead(`Pending/Rejected Kernel Specs (${pr.length})`));
    root.appendChild(this._card(pr.map(k => this._kernelBlock(k, undefined, undefined, k.status !== 'pending'))));

    return root;
  }

  private _topBar(): HTMLElement {
    const bar = document.createElement('div');
    bar.className = 'csTopBar';
    bar.appendChild(this._el('div', 'CYBERSHUTTLE', 'csTopTitle'));

    const info = this._el('div', 'i', 'csInfo');
    info.title = 'Info';
    bar.appendChild(info);
    return bar;
  }

  private _intro(): HTMLElement {
    return this._el(
      'div',
      'Manage and create kernels using your approved CyberShuttle compute allocations, directly inside JupyterLab.',
      'csIntro'
    );
  }

  private _subhead(text: string): HTMLElement {
    return this._el('div', text, 'csSubhead');
  }

  private _card(children: HTMLElement[]): HTMLElement {
    const card = document.createElement('div');
    card.className = 'csCard';
    children.forEach(c => card.appendChild(c));
    return card;
  }

  private _row(title: string, btnLabel: string, onClick: () => void): HTMLElement {
    const row = document.createElement('div');
    row.className = 'csRow';

    row.appendChild(this._el('div', title, 'csRowTitle'));

    const btn = document.createElement('button');
    btn.className = 'csBtn';
    btn.type = 'button';
    btn.textContent = btnLabel;
    // disable if busy for this title
    if (this._busy.get(title)) {
      btn.disabled = true;
      btn.style.opacity = '0.6';
    } else {
      btn.onclick = onClick;
    }
    row.appendChild(btn);

    if (this._busy.get(title)) {
      const sp = document.createElement('span');
      sp.className = 'csSpinner';
      row.appendChild(sp);
    }

    return row;
  }

  // UI Component for a kernel block
  private _kernelBlock(k: KernelSpecItem, actionLabel?: string, onAction?: () => void, showTrash?: boolean): HTMLElement {
    const block = document.createElement('div');
    block.className = 'csKernelBlock';

    const left = document.createElement('div');
    left.className = 'csKLeft';
    left.appendChild(this._el('div', k.name, 'csKName'));

    if (k.metadata?.length) {
      const ul = document.createElement('ul');
      ul.className = 'csMeta';
      k.metadata.forEach(line => {
        const li = document.createElement('li');
        li.textContent = line;
        ul.appendChild(li);
      });
      left.appendChild(ul);
    }

    const right = document.createElement('div');
    right.className = 'csKRight';

    if (showTrash) {
      const trash = document.createElement('button');
      trash.className = 'csTrash';
      trash.type = 'button';
      trash.title = 'Delete';
      trash.textContent = '🗑';
      trash.onclick = () => console.log('delete', k.name);
      right.appendChild(trash);
    }

    if (k.status === 'pending' || k.status === 'rejected') {
      const pill = document.createElement('span');
      pill.className = `csPill csPill-${k.status}`;
      pill.textContent = k.status === 'pending' ? 'Pending' : 'Rejected';
      right.appendChild(pill);
    } else if (actionLabel && onAction) {
      const btn = document.createElement('button');
      btn.className = 'csBtnPrimary';
      btn.type = 'button';
      btn.textContent = actionLabel;
      // disable if busy
      if (this._busy.get(k.name)) {
        btn.disabled = true;
        btn.style.opacity = '0.6';
      } else {
        btn.onclick = onAction;
      }
      right.appendChild(btn);

      if (this._busy.get(k.name)) {
        const sp = document.createElement('span');
        sp.className = 'csSpinner';
        right.appendChild(sp);
      }
    }

    block.appendChild(left);
    block.appendChild(right);
    return block;
  }

  private _el<K extends keyof HTMLElementTagNameMap>(tag: K, text: string, cls?: string): HTMLElementTagNameMap[K] {
    const el = document.createElement(tag);
    if (cls) el.className = cls;
    el.textContent = text;
    return el;
  }
}