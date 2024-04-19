# Potential ONNX model supply-chain attack and mitigation

Currently projects utilising the (unverified) model inswapper_128.onnx are ripe for a supply-chain attack.

Although arbitrary code execution is not (knowingly) possible within the binary data of an onnx model, a payload can/may 
be embedded, then at a later stage deserialised and invoked.

Code does not have to be malicious for a vulnerability to exist.

tldr;
- The initial concern was responsibly disclosed (and dismissed). The follow-up... less so.
- This repository contains two (soon to be three) valid proof of concepts, and their respective solutions. 
- We still do not know the contents of inswapper_128.onnx, or if the distributed commonly-used version is provably authentic.
- Publishers should ensure that commits to their git repositories are cryptographically signed.
- Publishers should provide transparency of changes to models, in a way that a user can reproduce themselves.
- Publishers of ML models, and tools that utilise them, should document the checksum hashes of the models in question.
- Users of such models should verify these checksums and remain cautious to this idea (see below on how-to guide).
- The community must be open to feedback and criticism, to discuss such ideas freely.
- Safety must come first over reputation.

## Preface

This repository serves as a proof of concept for such claims, and a consideration 
for mitigation of such a risk.

The community seems very uptight about the idea of what is and what isn't possible.
Recently the open-source space witnessed a long-play attack on the popular xz utils library.

Supply-chain attacks can be subtle, played out over a long period of time, and provide a massive attack surface for bad actors.

The intention of this write-up/POC is not to disparage the excellent work of well-respected contributors 
of these open-source projects, albeit to assist them and keep the community safe from harm.

This is not meant to cause reputational damage to any project in particular, but to address a 
rather large elephant in the room, that has been ignored for far too long; - 
that there is an unverified inswapper_128.onnx, the contents unknown, discovered in the wild.

It had been discussed that the model may be manipulated further at a later stage, and would have the
potential to become a risk later on - recently the model has been updated (undocumented change) and 
this has forced my hand to sound off loudly, and to prove the concept - the reason for this repo.

Hopefully it will create a shift in thinking and improve the security posture of many 
open-source projects going forwards.

## Plan of execution - what's the actual risk here?

In order to carry out such an attack, one would have to;

- attach serialised payload to the model (see below)
- provide modified onnx model to community (quietly)
- at a later stage, update a an application or library codebase to deserialise and eval the payload embedded within the model
- even the output of an image could embed the payload to be used in some other tool in a pipeline, by utilising steganography

## Payload vectors / Proof of concept

### Setup
 
```bash
python3.10 -m venv ./.venv
source ./.venv/bin/activate
pip install requirements.txt

# download the onnx model found inside (./models/test/test_sigmoid.onnx) from the onnx official repo;
# https://github.com/onnx/onnx/blob/main/onnx/backend/test/data/node/test_sigmoid/model.onnx
#sha256 - c9ea45be3dd00fd43865a739458c74c1f7c7fd325faf8294009f43ae9c0628dd

# run one of the scripts;

## Vector 1 - payload stored in metadata  
python ./code/metadata-attack-vector/sigmoid_attach_metadata.py
## To execute the payload inside the metadata of the model;
python ./code/metadata-attack-vector/sigmoid_exec.py

## Vector 2 - payload embedded in numpy array 
python ./code/constant-attack-vector/sigmoid_attach_constant.py
## To execute the payload inside the constant node of the model;
python ./code/constant-attack-vector/sigmoid_exec_onnxruntime.py

``` 

### vector #1 - Payload embedded in metadata

A simple trick, a payload may be embedded within the metadata of a model, can be further serialised and/or obfuscated.

Attach payload to an existing model;
```bash
python ./code/metadata-attack-vector/sigmoid_attach_metadata.py
```

The third party can run an `eval()` on the string to execute python code.
```bash
python ./code/constant-attack-vector/sigmoid_exec.py
printing metadata props;
Key: producer_name, Value: print("popping calc.exe")
popping calc.exe
```

Fairly obvious to spot, unless buried within a huge model or obfuscated further.

The concept has now been proven.

Resolution: Strip metadata from models
Resolution: Checksums should be published in order to ensure the model hasn't been tampered with.

### vector #2 - Payload embedded as serialised numpy array, added as a constant value inside original graph

Unlike the metadata payload above, the Constant payload is embedded and not visible at a first glance.
It embeds a payload as a numpy array to be held inside a Constant node instead the onnx model's graph.

Converting payload to a numpy array and then attaching it to an existing model;
```bash
python ./example/constant-attack-vector/sigmoid_attach_constant.py
```

The third party can again deserialise the numpy array and run an `eval()` on the string 
to execute python code.
```bash
python ./code/constant-attack-vector/sigmoid_exec_onnxruntime.py
Name of the constant tensor: encoded_array_1_1000_output
Value of the constant tensor:
[112 114 105 110 116  40  34 112 111 112 112 105 110 103  32  99  97 108
  99  46 101 120 101  34  41]
payload: print("popping calc.exe")
popping calc.exe
``` 

The concept has now been proven.

Resolution: remove hanging constant nodes [10]
Resolution: audit code of third-party tools before running

### Vector #3 - Payload embedded as serialised numpy array, added as a final-step operation of an existing graph

This one is a little trickier - when dealing with images or audio, a custom operation can be added towards the end of a graph, or within 
multiple nodes, the payload eventually layered within the output.
Without interrupting or causing suspicion, an attacker can leverage steganography and then deserialise the payload later.

```python
# proof of concept TBC
```

Resolution: for models that create images and audio, pass model output through a random low-noise filter

## A quick how-to guide on checking the integrity of your models;

Most authors of models will share the checksum hash of the files that they distribute, so you can 
verify the file you have downloaded is authentic.

The instructions below are for a Linux terminal, so I hope others will contribute methods for Windows!

The "original" inswapper onnx model;

```bash
sha256sum ./inswapper_128.onnx
e4a3f08c753cb72d04e10aa0f7dbe3deebbf39567d4ead6dce08e98aa49e16af ./inswapper_128.onnx
```

The latest inswapper_128.onnx model inside the FaceFusion models repo;

```bash
sha256sum ./inswapper_128.onnx
0fa95f167682b4f61edf24f8d66c46b4ab130e8be058f00c8150e6d0170ca72f  ./inswapper_128.onnx
```

As the checksums no longer match, so we can verify that the model has been changed, but in this instance, 
the change ~~has not been disclosed~~ was disclosed, but explanation and source code has since been removed.

Users are not currently able to reproduce the change. The contents of inswapper_128.onnx are still unknown and not reproducible.
This is not opensource. 

## Mitigation

- publish checksums of the current models to ensure integrity
- possibility to post-process the model to add low random noise to the output of the graph (audio and visual)
- strip the metadata of the model at runtime
- an audit of inswapper_128.onnx (all versions)
- sandbox the model, or application inside a Docker container with no outgoing network access

## Reflection

On a personal note, I would like to reiterate that there has been no acussation of foul play from the fine developers of Facefusion.
I will reiterate that the "original" inswapper_128.onnx _MAY_ be unsafe, that further changes to this file _MAY_ be unsafe. 

Henry, I think your work on enhancing Roop has been excellent, but I have been consistent with the messaging in this regard - identifying the potential for this scenario very early over on the Roop repository.
I am in no way perfect, but the intention was pure, my mistake here is that I should have simply raised; "file has changed, why?"
The fact that I have tried my very best on multiple ocassions to get the discussion going on this, but have been dismissed heavily and even mistreated by some members of the community, is the reason for the abrupt messaging - you must admit that you do not know what lies within inswapper_128.onnx

Special thanks to the r/stablediffusion mods over on Discord for finding a balance, and mediation of a solution.

### Reference

#### History, timeline of events

- Roop is published by known security researcher @somed3v (that's an interesting twitter bio bro! [9]), with a pretrained model inswapper_128.onnx, contents unknown
- Google dorking for inswapper_128.onnx shows the checksum to appear in a Russian-language forum
- The creators of inswapper, Insightface, have since revoked the model from their repository, and refuse to publish the checksum of the file upon request []
- Raised a ticket/warning in Roop github repository (dismissed), tried to engage the team on discord (kick/banned)
- I then resign to warn others that Roop is viably unsafe [9]
- Some time passes
- YouTube content creators are now pushing Roop and variations - I try to disclose the vulnerability again; and again receive unwarranted pushback from community
- Some time passes
- The successor of Roop (Facefusion) has published a modified inswapper_128.onnx file (undocumented change) 
- After little to no success before, the time for responsible disclosure has now passed. Again I raise my concerns, this time in no uncertain terms over on r/stablediffusion, and try to find a middle-ground with a remedy on ticket on Facefusion github (dismissed, closed)
- The author of Facefusion refuses to acknowledge the risk, refuses to accept any contributions (from me) that would make the model safe. 
- The post on r/StableDiffusion has been removed, no explanation given [8]
- Facefusion Github issue has now been deleted by the Facefusion organisation, the python code that was used to update the model is now lost.
- Published details of attack vector and at least 2 methods/proofs of concept (this repo)

#### Resources

[1] https://hiddenlayer.com/research/weaponizing-machine-learning-models-with-ransomware/
[2] https://5stars217.github.io/2023-03-30-on-malicious-models/
[3] https://medium.com/featurepreneur/pickle-is-sour-lets-use-onnx-90c0805338ac
[4] https://github.com/ZhangGe6/onnx-modifier
[5] https://onnxruntime.ai/docs/api/python/auto_examples/plot_load_and_predict.html
[6] https://github.com/facefusion/facefusion/blob/master/facefusion/processors/frame/modules/face_swapper.py#L253
[7] https://github.com/facefusion/facefusion/issues/493
[8] https://archive.is/Cio8X
[9] https://web.archive.org/web/20221217024256/https://twitter.com/s0md3v
[10] https://github.com/microsoft/onnxruntime/issues/1899#issuecomment-840596510