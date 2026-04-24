import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from '../InsuranceCheckControl/components/App';
import '../InsuranceCheckControl/styles/globals.css';

const ensureTweaksPanel = (): void => {
  if (document.getElementById('tweaks-panel')) return;
  const panel = document.createElement('div');
  panel.id = 'tweaks-panel';
  panel.innerHTML = `
    <div class="tweak-title">Tweaks</div>
    <label>テーブル行の高さ<input type="range" id="tw-row-height" min="36" max="64" step="4" value="44"></label>
    <label>フォントサイズ<input type="range" id="tw-font-size" min="11" max="16" step="1" value="13"></label>
    <label>チャット分割比
      <select id="tw-chat-split">
        <option value="38">左38% / 右62%</option>
        <option value="42" selected>左42% / 右58%</option>
        <option value="50">左50% / 右50%</option>
      </select>
    </label>
  `;
  document.body.appendChild(panel);
};

ensureTweaksPanel();

const rootEl = document.getElementById('root');
if (!rootEl) {
  throw new Error('#root element not found');
}

createRoot(rootEl).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
