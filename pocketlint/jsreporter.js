// Copyright (C) 2009-2010 - Curtis Hovey <sinzui.is at verizon.net>
// This software is licensed under the MIT license (see the file COPYING).

function report_implied_names() {
    // Report about implied global names.
    var implied_names = [];
    for (var name in JSLINT.implied) {
        if (JSLINT.implied.hasOwnPropery(name)) {
            implied_names.push(name);
            }
        }
    if (implied_names.length > 0) {
        implied_names.sort()
        print('0::0::Implied globals:' + implied_names.join(', '));
        }
    }


function report_lint_errors() {
    // Report about lint errors.
    for (var i = 0; i < JSLINT.errors.length; i++) {
        var error = JSLINT.errors[i];
        if (error === null) {
            print('0::0::JSLINT had a fatal error.');
            }
        print(++error.line + '::' + ++error.character + '::' + error.reason);
        }
    }


function main(source_script) {
    // Lint the source and report errors.
    var result = JSLINT(source_script);
    if (! result) {
        report_lint_errors();
        report_implied_names();
        }
    }


main(arguments[0])
