% версии кодируются как major*100 + minor*10 + patch; 0 = пакет не установлен
var {0, 100}: root;
var {0, 100, 110}: foo;
var {0, 100}: left;
var {0, 100}: right;
var {0, 100, 200}: shared;
var {0, 100, 200}: target;

constraint root = 100;
% root 1.0.0 -> foo ^1.0.0, target ^2.0.0
constraint root = 100 -> (foo >= 100 /\ foo < 200) /\ (target >= 200 /\ target < 300);
% foo 1.1.0 -> left ^1.0.0, right ^1.0.0
constraint foo = 110 -> (left >= 100 /\ left < 200) /\ (right >= 100 /\ right < 200);
% left 1.0.0 -> shared >=1.0.0
constraint left = 100 -> shared >= 100;
% right 1.0.0 -> shared <2.0.0
constraint right = 100 -> (shared > 0 /\ shared < 200);
% shared 1.0.0 -> target ^1.0.0
constraint shared = 100 -> (target >= 100 /\ target < 200);

solve maximize foo;
output ["root=\(root) foo=\(foo) left=\(left) right=\(right) shared=\(shared) target=\(target)\n"];
