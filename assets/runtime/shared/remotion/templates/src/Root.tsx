import React from 'react';
import {AbsoluteFill, Audio, Composition, registerRoot, staticFile, useCurrentFrame} from 'remotion';
import {CUES, TOTAL_FRAMES} from '../../build/cues';
import project from '../../project.json';
import {C} from './palette';
import {Scene} from './Scene';
// Replace beat-level captions with phrase timings anchored to real audio before delivery.
const Video: React.FC = () => {
  const frame = useCurrentFrame();
  const cue = CUES.find(c => frame >= c.startFrame && frame < c.startFrame+c.durationFrames);
  return <AbsoluteFill style={{background:C.bg,color:C.ink,fontFamily:'"PingFang SC", "Microsoft YaHei", sans-serif'}}>
    <Scene />
    {CUES.length > 0 && <Audio src={staticFile('audio/voiceover.wav')} />}
    {cue && <div style={{position:'absolute',bottom:72,left:120,right:120,display:'flex',justifyContent:'center'}}>
      <div style={{fontSize:40,lineHeight:1.4,background:C.ink,color:C.card,padding:'14px 30px',borderRadius:14}}>{cue.text}</div>
    </div>}
  </AbsoluteFill>;
};
const Root: React.FC = () => <Composition id={project.compositionId} component={Video} durationInFrames={TOTAL_FRAMES} {...project.config.video} />;
registerRoot(Root);
