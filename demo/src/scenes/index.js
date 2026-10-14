import s08 from './s08_meeting.js';
import s05 from './s05_tasks.js';
import s03 from './s03_reveal.js';
import s02 from './s02_lobby.js';
import s06 from './s06_eliminate.js';
import s07 from './s07_report.js';
import s10 from './s10_win.js';
import s00 from './s00_title.js';
import s09 from './s09_ghost.js';
import s01 from './s01_town.js';
import s04 from './s04_impostor.js';

const stub = (id, title, chapter) => ({ id, title, chapter, story: 'TODO', criteria: [], steps: [{ label: 'todo', async run() {} }], async enter(ctx) { ctx.caption(`${title} (not built yet)`); } });
export const SCENES = [
  s00, s01, s02, s03, s04,
  s05, s06, s07, s08, s09, s10,
];
