import { Signal } from '@lumino/signaling';
import { Widget } from '@lumino/widgets';

export interface ExistingKernelInfo {
  url: string;
  token?: string;
  name?: string;
}

export class AddExistingKernelForm extends Widget {
  readonly backRequested = new Signal<this, void>(this);
  readonly cancelRequested = new Signal<this, void>(this);
  readonly connectSubmitted = new Signal<this, ExistingKernelInfo>(this);

  private _url!: HTMLInputElement;
  private _token!: HTMLInputElement;
  private _kernelName!: HTMLInputElement;
  private _progress!: HTMLElement;

  constructor() {
    super();
    this.id = 'cs-add-existing-form';
    this.addClass('csKernelPanel');
    this.hide();
    this._render();
  }

  private _render(): void {
    this.node.textContent = '';
    this.node.appendChild(this._build());
  }

  private _build(): HTMLElement {
    const root = document.createElement('div');
    root.className = 'csRoot csFormRoot';

    // Top: Back + Title
    const top = document.createElement('div');
    top.className = 'csFormTop';

    const back = document.createElement('button');
    back.className = 'csBackBtn';
    back.type = 'button';
    back.textContent = '← Back';
    back.onclick = () => this.backRequested.emit(undefined);

    const title = document.createElement('div');
    title.className = 'csFormTitle';
    title.textContent = 'Add an Existing Kernel';

    top.appendChild(back);
    top.appendChild(title);
    root.appendChild(top);

    // Instructions box
    const instr = document.createElement('div');
    instr.className = 'csInstructions';
    instr.innerHTML = `
      <strong>Instructions</strong>
      <ul>
        <li>If you already have a running kernel outside CyberShuttle, you can connect it here.</li>
        <li>Provide the kernel's URL and access token to authenticate.</li>
        <li>Once connected, the kernel will appear and can be used like any other JupyterLab kernel.</li>
      </ul>`;
    root.appendChild(instr);

    // Form fields
    const form = document.createElement('div');
    form.className = 'csForm';

  this._kernelName = document.createElement('input');
  this._kernelName.className = 'csInput';
  this._kernelName.placeholder = 'Kernel name (optional)';
  form.appendChild(this._fieldRow(this._kernelName));

  this._url = document.createElement('input');
  this._url.className = 'csInput';
  this._url.placeholder = 'URL';
  form.appendChild(this._fieldRow(this._url));

  this._token = document.createElement('input');
  this._token.className = 'csInput';
  this._token.placeholder = 'Access token';
  form.appendChild(this._fieldRow(this._token));

    root.appendChild(form);

    // Footer buttons
    const footer = document.createElement('div');
    footer.className = 'csFormFooter';

    const cancel = document.createElement('button');
    cancel.className = 'csCancel';
    cancel.type = 'button';
    cancel.textContent = 'Cancel';
    cancel.onclick = () => this.cancelRequested.emit(undefined);

    const connect = document.createElement('button');
    connect.className = 'csRequest';
    connect.type = 'button';
    connect.textContent = 'Connect';
    connect.onclick = () => this._onConnect();

    footer.appendChild(cancel);
    footer.appendChild(connect);
    root.appendChild(footer);

    // Progress area
    this._progress = document.createElement('div');
    this._progress.className = 'csConnectProgress';
    this._progress.style.display = 'none';
    this._progress.innerHTML = `
      <div class="csConnectingText">Connecting...</div>
      <div class="csProgressBar"><div class="csProgressFill" style="width:0%"></div></div>
    `;
    root.appendChild(this._progress);

    return root;
  }

  private _fieldRow(control: HTMLElement): HTMLElement {
    const wrapper = document.createElement('div');
    wrapper.className = 'csFormRow';

    const left = document.createElement('div');
    left.className = 'csRowNum';
    left.textContent = '';

    const right = document.createElement('div');
    right.className = 'csRowRight';

    right.appendChild(control);

    wrapper.appendChild(left);
    wrapper.appendChild(right);
    return wrapper;
  }

  private async _onConnect(): Promise<void> {
    const info: ExistingKernelInfo = {
      url: this._url.value.trim(),
      token: this._token.value.trim() || undefined,
      name: this._kernelName.value.trim() || undefined
    };
    // show progress UI
    this._progress.style.display = 'block';
    const fill = this._progress.querySelector('.csProgressFill') as HTMLElement;
    let pct = 0;
    const t = setInterval(() => {
      pct = Math.min(90, pct + Math.floor(Math.random() * 20) + 10);
      fill.style.width = `${pct}%`;
    }, 300);

    try {
      // emit submitted so host can attempt connect; host may call back to update progress or finish
      this.connectSubmitted.emit(info);
    } finally {
      // simulate finish animation a bit later (host may call hideProgress)
      clearInterval(t);
      fill.style.width = `100%`;
      setTimeout(() => (this._progress.style.display = 'none'), 500);
    }
  }

  public showProgress(percent: number): void {
    this._progress.style.display = 'block';
    const fill = this._progress.querySelector('.csProgressFill') as HTMLElement;
    fill.style.width = `${percent}%`;
  }
}
