// src/CyberShuttlePanel.ts
import { StackedPanel } from '@lumino/widgets';
import { KernelList } from './KernelList';
import { RequestKernelForm } from './RequestKernelForm';
import { AddExistingKernelForm, ExistingKernelInfo } from './AddExistingKernelForm';
import { JupyterFrontEnd } from '@jupyterlab/application';
import { KernelSpecItem } from './Common';

export class CyberShuttlePanel extends StackedPanel {
  private _list: KernelList;
  private _form: RequestKernelForm;
  private _existingForm: AddExistingKernelForm;
  private _app: JupyterFrontEnd;

  constructor(app: JupyterFrontEnd) {
    super();
    this._app = app;
    this.id = 'cybershuttle-panel';
    this.title.label = 'CyberShuttle';
    this.title.closable = true;
    this.addClass('csShell');

    this._list = new KernelList(app);
    this._form = new RequestKernelForm();
    this._existingForm = new AddExistingKernelForm();

    this.addWidget(this._list);
    this.addWidget(this._form);
    this.addWidget(this._existingForm);

    this._showList();

    // Switch to form when user clicks "+ Add new"
    this._list.addNewRequested.connect(() => this._showForm());
    this._list.addExistingRequested.connect(() => this._showExistingForm());

    // When user clicks Connect on an available kernel in the list
    this._list.connectRequested.connect((_sender, kernelSpecItem) => {
      (async () => {
        try {
          // mark UI busy for this kernel id
          this._list.setBusy(kernelSpecItem.id, true);
          const xsrf = this._getXsrfToken();

          const installResp = await fetch('/cslx/api/install-kernelspec', {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json', ...(xsrf ? { 'X-XSRFToken': xsrf } : {}) },
            body: JSON.stringify({ 
              name: kernelSpecItem.name, 
              id: kernelSpecItem.id, 
              url: kernelSpecItem.url, 
              token: kernelSpecItem.token })
          });

          console.log('Install response:', installResp);
          await (this._app.serviceManager.kernelspecs as any).refreshSpecs()
          this._list.updateKernelSpecStatus(kernelSpecItem.id, 'connected');
          this._list.setBusy(kernelSpecItem.id, false);
        } catch (e) {
          console.error('[CyberShuttle] failed to start kernel from connect click', e);
          this._list.setBusy(kernelSpecItem.id, false);
        }
      })();
    });

    // When user clicks Disconnect in the list
    this._list.disconnectRequested.connect((_sender, kernelSpecItem) => {
      (async () => {
        try {
            // mark UI busy for this kernel name
            console.log('[CyberShuttle] disconnecting kernel ', kernelSpecItem.id, ' with name ', kernelSpecItem.name);
            this._list.setBusy(kernelSpecItem.id, true);

            // find sessionId by display name (we store sessions keyed by sessionId)
            try {
              const xsrf = this._getXsrfToken();
              const resp = await fetch('/cslx/api/uninstall-kernelspec', {
                method: 'POST',
                credentials: 'same-origin',
                headers: { 'Content-Type': 'application/json', ...(xsrf ? { 'X-XSRFToken': xsrf } : {}) },
                body: JSON.stringify({ name: kernelSpecItem.name, id: kernelSpecItem.id })
              });
              if (!resp.ok) {
                const text = await resp.text();
                console.warn('[CyberShuttle] uninstall kernelspec failed', resp.status, text);
              } else {
                const j = await resp.json();
                console.log('[CyberShuttle] uninstall result', j);
              }
            } catch (e) {
              console.error('[CyberShuttle] uninstall kernelspec request failed', e);
            }
            await (this._app.serviceManager.kernelspecs as any).refreshSpecs()

            // Update UI to mark kernel as available
            this._list.updateKernelSpecStatus(kernelSpecItem.id, 'available');
            this._list.setBusy(kernelSpecItem.id, false);
        } catch (e) {
          console.error('[CyberShuttle] failed to disconnect kernel', e);
          // ensure busy cleared on error
          this._list.setBusy(kernelSpecItem.id, false);
        }
      })();
    });

    // Back/cancel returns to list
    this._form.backRequested.connect(() => this._showList());
    this._form.cancelRequested.connect(() => this._showList());
    this._existingForm.backRequested.connect(() => this._showList());
    this._existingForm.cancelRequested.connect(() => this._showList());
    this._existingForm.connectSubmitted.connect((_s, info: ExistingKernelInfo) => {
      // Show progress on existing form and add as an available kernel entry with metadata
      this._existingForm.showProgress(30);
      // prefer a user-provided kernel name, otherwise derive from the URL host
      const displayName = info.name && info.name.trim() ? info.name.trim() : info.url ? new URL(info.url).hostname : `external-${Date.now()}`;
      const listName = `External: ${displayName}`;

      setTimeout(() => {
        // Add to the Available Kernels list and include url/token in the stored object
        const id = `external-${Date.now()}`;
        const newKernelSpecItem: KernelSpecItem = { 
          id: id, 
          name: listName, 
          status: 'available', metadata: [''], 
          url: info.url || '', 
          token: info.token || '' };
        this._list.addKernelSpecItem(newKernelSpecItem);
        this._showList();
      }, 100);
    });

    // Handle submission (then go back to list, or keep form if you want)
    this._form.requestSubmitted.connect((_sender, req) => {
      console.log('[CyberShuttle] request submitted', req);
      this._showList();
      // TODO: Add a pending kernel entry in the UI
    });
  }

  /**
   * Read XSRF token from document cookies. Jupyter server uses a cookie named
   * '_xsrf' (or sometimes 'XSRF-TOKEN'). Return the token or empty string.
   */
  private _getXsrfToken(): string {
    if (typeof document === 'undefined' || !document.cookie) return '';
    const m = document.cookie.match(/(?:^|; )(_xsrf|XSRF-TOKEN)=([^;]+)/);
    if (m && m.length > 2) return decodeURIComponent(m[2]);
    return '';
  }


  private _showList(): void {
    this._list.show();
    this._form.hide();
    this._existingForm.hide();
    this._list.activate();
  }

  private _showForm(): void {
    this._form.show();
    this._existingForm.hide();
    this._list.hide();
    this._form.activate();
  }

  private _showExistingForm(): void {
    this._existingForm.show();
    this._list.hide();
    this._existingForm.activate();
  }
}


