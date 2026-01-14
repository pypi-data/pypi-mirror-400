Please check the Issue Tracker if your bug is already listed before reporting.

## Summary

(Summarize the encountered bug)

## Steps to reproduce

(Explain step by step how to reproduce the bug. If you don't know, explain how you encountered it.)

## Bug behavior

(What actually happens)


## What is the expected correct behavior?

(What you should see instead)

## Relevant logs and/or screenshots

(Paste any relevant logs - please use code blocks (```) to format console output, logs, and code, as
it's very hard to read otherwise.)

## Possible Fixes

(If you have an idea how to fix the bug or which part/line of the code might be responsible please share ;) )

## Labels

Please assign labels to the issue by uncommenting approiate lines:

### Reproducing the bug
If cannot reproduce the bug comment out the first line and uncomment the second.
/label ~"Bug::normal"
<!-- /label ~"Bug::investigation" -->

### Area of the bug

If possible label the area the bug is occuring in:
    - Packaging (you can only use one)
     <!-- /label ~"Packaging::pip" -->
     <!-- /label ~"Packaging::conda" -->
     <!-- /label ~"Packaging::general" -->
    - Build system
     <!-- /label ~"Build system" -->
    - Documentation
     <!-- /label ~"Documentation" -->
    - Parser (of the KatScript) Use Parser::legacy if you are parsing legacy files
     <!-- /label ~"Parser" -->
     <!-- /label ~"Parser::legacy" -->
    - Plotting
     <!-- /label ~"Plotting" -->
    - Testing (for issues with the automated tests)
     <!-- /label ~"Testing" -->
    - User interface
     <!-- /label ~"User interface" -->

### Operating system

Add a label for the operating system you are using Finesse on.
<!-- ~label /"OS::Linux -->
<!-- ~label /"OS::MacIntel -->
<!-- ~label /"OS::MacAppleSilicon -->
<!-- ~label /"OS::Windows -->

### Urgency

If the bug is preventing Finesse from being used, for example if it produces seemingly valid but incorrect results, add this label.
<!-- /label ~"Priority::Urgent" -->
