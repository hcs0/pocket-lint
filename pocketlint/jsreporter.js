function report_implied_names() {
    /* Report about implied global names. */
    var implied_names = [];
    for (var name in JSLINT.implied) {
        if (JSLINT.implied.hasOwnPropery(name)) {
            implied_names.push(name);
            }
        }
    if (implied_names.length > 0) {
        implied_names.sort();
        print('0::0::Implied globals:' + implied_names.join(', '));
        }
    }


function report_lint_errors() {
    /* Report about lint errors. */
    for (var i = 0; i < JSLINT.errors.length; i++) {
        var error = JSLINT.errors[i];
        if (error === null) {
            print('0::0::JSLINT had a fatal error.');
            }
        var line_no = error.line + 1;
        var char_no = error.character + 1;
        print(line_no + '::' + char_no + '::' + error.reason);
        }
    }


var source_script = arguments[0];
var result = JSLINT(source_script);
if (! result) {
    report_lint_errors();
    report_implied_names();
    }
