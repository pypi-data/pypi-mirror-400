import { Signal } from '@lumino/signaling';
import { Widget } from '@lumino/widgets';
import { KernelRequest } from './Common';

export class RequestKernelForm extends Widget {
  readonly backRequested = new Signal<this, void>(this);
  readonly cancelRequested = new Signal<this, void>(this);
  readonly requestSubmitted = new Signal<this, KernelRequest>(this);

  // controls
  private _name!: HTMLInputElement;
  private _allocation!: HTMLSelectElement;
  private _compute!: HTMLSelectElement;
  private _queue!: HTMLSelectElement;

  private _nodes!: HTMLInputElement;
  private _cores!: HTMLInputElement;
  private _wall!: HTMLInputElement;
  private _mem!: HTMLInputElement;

  constructor() {
    super();
    this.id = 'cybershuttle-request-form';
    this.addClass('csKernelPanel');
    this.hide(); // start hidden; panel shows list first
    this._render();
  }

  private _render(): void {
    this.node.textContent = '';
    this.node.appendChild(this._build());
  }

  private _build(): HTMLElement {
    const root = document.createElement('div');
    root.className = 'csRoot csFormRoot';

    // Top row: Back + Title
    const top = document.createElement('div');
    top.className = 'csFormTop';

    const back = document.createElement('button');
    back.className = 'csBackBtn';
    back.type = 'button';
    back.textContent = '← Back';
    back.onclick = () => this.backRequested.emit(undefined);

    const title = document.createElement('div');
    title.className = 'csFormTitle';
    title.textContent = 'Requesting a new Kernel';

    top.appendChild(back);
    top.appendChild(title);
    root.appendChild(top);

    // Fields
    const form = document.createElement('div');
    form.className = 'csForm';

    // 1) Name
    this._name = document.createElement('input');
    this._name.className = 'csInput';
    this._name.placeholder = 'Add a Name';
    form.appendChild(this._rowNum(1, this._name));

    // 2) Allocation
    this._allocation = this._select(['Select an Allocation', 'Allocation A', 'Allocation B']);
    form.appendChild(this._rowNum(2, this._allocation));

    // 3) Compute resource
    this._compute = this._select(['Select a Compute Resource', 'CPU', 'GPU']);
    form.appendChild(this._rowNum(3, this._compute));

    // 4) Queue
    this._queue = this._select(['gpu-shared', 'cpu-shared', 'gpu-dedicated']);
    const queueRow = this._rowNum(4, this._queue, 'Select a Queue :');
    const hint = document.createElement('div');
    hint.className = 'csRightHint';
    hint.textContent = 'Expanse GPU (NV)';
    queueRow.querySelector('.csRowRight')?.appendChild(hint);
    form.appendChild(queueRow);

    // 5) Node count (stepper)
    this._nodes = this._numInput(1);
    form.appendChild(this._stepRow(5, 'Node count :', this._nodes, 1, 'Max Allowed Nodes = 1'));

    // 6) Total core count
    this._cores = this._numInput(1);
    form.appendChild(this._stepRow(6, 'Total Core Count :', this._cores, 39, 'Max Allowed Cores = 39. There are 39 cores per node.'));

    // 7) Wall time (minutes)
    this._wall = this._numInput(0);
    form.appendChild(this._stepRow(7, 'Wall Time Limit :', this._wall, 0, 'Max Allowed Wall Time = 0 minutes', 'Minutes'));

    // 8) Memory (MB)
    this._mem = this._numInput(0);
    form.appendChild(this._stepRow(8, 'Total Physical Memory', this._mem, 128000, 'Max Physical Memory = 128000 MB', 'MB'));

    root.appendChild(form);

    // Footer buttons
    const footer = document.createElement('div');
    footer.className = 'csFormFooter';

    const cancel = document.createElement('button');
    cancel.className = 'csCancel';
    cancel.type = 'button';
    cancel.textContent = 'Cancel';
    cancel.onclick = () => this.cancelRequested.emit(undefined);

    const request = document.createElement('button');
    request.className = 'csRequest';
    request.type = 'button';
    request.textContent = 'Request';
    request.onclick = () => this._submit();

    footer.appendChild(cancel);
    footer.appendChild(request);
    root.appendChild(footer);

    return root;
  }

  private _submit(): void {
    const req: KernelRequest = {
      name: this._name.value.trim() || 'Unnamed Kernel',
      allocation: this._allocation.value,
      computeResource: this._compute.value,
      queue: this._queue.value,
      nodeCount: Number(this._nodes.value || 0),
      coreCount: Number(this._cores.value || 0),
      wallMinutes: Number(this._wall.value || 0),
      memoryMB: Number(this._mem.value || 0)
    };
    this.requestSubmitted.emit(req);
  }

  private _rowNum(n: number, control: HTMLElement, labelText?: string): HTMLElement {
    const row = document.createElement('div');
    row.className = 'csFormRow';

    const left = document.createElement('div');
    left.className = 'csRowNum';
    left.textContent = `${n}.`;

    const right = document.createElement('div');
    right.className = 'csRowRight';

    if (labelText) {
      const label = document.createElement('div');
      label.className = 'csLabel';
      label.textContent = labelText;
      right.appendChild(label);
    }

    right.appendChild(control);

    row.appendChild(left);
    row.appendChild(right);
    return row;
  }

  private _stepRow(
    n: number,
    label: string,
    input: HTMLInputElement,
    max: number,
    helper: string,
    unitText?: string
  ): HTMLElement {
    const wrapper = document.createElement('div');
    wrapper.className = 'csFormRow';

    const left = document.createElement('div');
    left.className = 'csRowNum';
    left.textContent = `${n}.`;

    const right = document.createElement('div');
    right.className = 'csRowRight';

    const lbl = document.createElement('div');
    lbl.className = 'csLabel';
    lbl.textContent = label;

    const step = document.createElement('div');
    step.className = 'csStepper';

    const fieldWrap = document.createElement('div');
    fieldWrap.className = 'csStepperFieldWrap';

    // unit label (like "Minutes" / "MB") sitting in the input row
    if (unitText) {
      const unit = document.createElement('div');
      unit.className = 'csUnit';
      unit.textContent = unitText;
      fieldWrap.appendChild(unit);
    }

    fieldWrap.appendChild(input);

    const minus = document.createElement('button');
    minus.className = 'csStepBtn';
    minus.type = 'button';
    minus.textContent = '−';
    minus.onclick = () => this._bump(input, -1, max);

    const plus = document.createElement('button');
    plus.className = 'csStepBtn';
    plus.type = 'button';
    plus.textContent = '+';
    plus.onclick = () => this._bump(input, +1, max);

    step.appendChild(fieldWrap);
    step.appendChild(minus);
    step.appendChild(plus);

    const help = document.createElement('div');
    help.className = 'csHelp';
    help.textContent = helper;

    right.appendChild(lbl);
    right.appendChild(step);
    right.appendChild(help);

    wrapper.appendChild(left);
    wrapper.appendChild(right);
    return wrapper;
  }

  private _bump(input: HTMLInputElement, delta: number, max: number): void {
    const cur = Number(input.value || 0);
    const next = Math.max(0, Math.min(max, cur + delta));
    input.value = String(next);
  }

  private _numInput(initial: number): HTMLInputElement {
    const i = document.createElement('input');
    i.className = 'csInput csNum';
    i.type = 'number';
    i.min = '0';
    i.value = String(initial);
    return i;
  }

  private _select(options: string[]): HTMLSelectElement {
    const s = document.createElement('select');
    s.className = 'csSelect';
    options.forEach(opt => {
      const o = document.createElement('option');
      o.value = opt;
      o.textContent = opt;
      s.appendChild(o);
    });
    return s;
  }
}