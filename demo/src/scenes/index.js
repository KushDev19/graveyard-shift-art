import s08 from './s08_meeting.js';
import s05 from './s05_tasks.js';

const stub = (id, title, chapter) => ({ id, title, chapter, story: 'TODO', criteria: [], steps: [{ label: 'todo', async run() {} }], async enter(ctx) { ctx.caption(`${title} (not built yet)`); } });
export const SCENES = [
  stub(0, 'Title', 'INTRO'), stub(1, 'Town & arcade', 'US3'), stub(2, 'Locker lobby', 'US3'), stub(3, 'Crew reveal', 'US3'), stub(4, 'Impostor reveal', 'US3'),
  s05, stub(6, 'Impostor eliminate', 'US3'), stub(7, 'Report body', 'US2'), s08, stub(9, 'Ghost view', 'EDGE'), stub(10, 'Win', 'END'),
];
