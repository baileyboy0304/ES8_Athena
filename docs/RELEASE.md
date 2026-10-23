# Private candidate → community release

The owner approved the **private** GitHub transfer on 23 October 2026, after reviewing
the package. This enables the Linux installation walkthrough. The repository is
`baileyboy0304/ES8_Athena`. No scheduled publishing is configured. Community publication requires
acceptance after the clean-install tests and is a separate later action.

Before the private push, review tracked files, notices, file sizes and the limited
packaging checks. Exclude all private installation inputs. Use a recursive clone
on Linux; see [handover](LINUX-HANDOVER.md).

Before community publication:

1. Finish `ACCEPTANCE.md` and fix installation/doc issues from the owner.
2. Review licences/notices and confirm redistribution of all compiled dependencies.
   Keep firmware, root archives, APK exports, private signing keys and backups out.
3. Decide how to distribute the prototype APKs and future signed updates. They are
   existing development-signed builds. Private signing keys were deliberately not
   copied; changing signers breaks in-place updates. Establish release signing
   before asking the community to adopt a long-term installation.
4. Review compatibility of the separate installed-firewall adaptation with upstream.
   Never claim it is a released EDA feature. The source/installer stay unchanged;
   leave automatic EDA updates off while using this candidate adaptation.
5. Check `git status --ignored` and `git ls-files`; explicitly look for local paths,
   credentials, device IDs, account information and private captures.
6. Run `python install.py verify` and the small offline installer tests. Record the
   tested HA/MA/VA/device versions. Do not label the entire inherited test suite green.
7. Use a release archive or release assets for bulky APKs if preferred. The included
   manifest provides integrity, not publisher authentication/signature verification.

The checked-in EDA source contains its normal support for other Echo models.
That is upstream source, not a second installation path offered by this product.
These instructions select **athena only**. The bundled VACAV integration retains its
existing supported roles so Portal support remains available; ES8 instructions
select `standard_upstream_eda` only.

Known wider release gates from the trial: update/fallback/uninstall lifecycle,
full EDA controls/status parity, timers/follow-up/barge-in, long-term music grouping,
other Android firmware and HA compatibility. The initial owner walkthrough is the
next gate, not a claim those broader cases have already been validated.
