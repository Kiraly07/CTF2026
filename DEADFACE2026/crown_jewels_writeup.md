# Crown Jewels — De Monne Breach (75 pts)

The attacker copied several documents off the executive share. What was the first PDF read?

## How I solved it

In the pcap, the attacker (10.77.10.66) tree-connects to the real file server's executive share — `\\10.77.10.30\executive` at frame 6733. Then list the SMB2 CREATE requests against that share in time order:

```
tshark -r demonne.pcap -Y "smb2.cmd==5 && smb2.tree" \
  -T fields -e frame.number -e smb2.filename | sort -n
```

```
frame 7404: annual_report.pdf            <- first PDF, read at 7409/7482
frame 8321: executive_risk_register.xlsx
frame 9086: board_transition_timeline.pdf
frame 9738: succession_vote_draft.pdf
```

Four documents, and the first one opened — PDF or otherwise — is `annual_report.pdf`. The same file that shows up being zipped and exfiled in Public Offering, which cross-confirms it.

## Flag

```
deadface{annual_report.pdf}
```
