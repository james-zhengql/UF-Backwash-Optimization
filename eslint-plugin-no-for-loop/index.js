
module.exports = {
  rules: {
    "no-for-loop": {
      create: function (context) {
        return {
          ForStatement(node) {
            context.report({
              node,
              message: "Do not use for() statements, use an appropriate iterator like forEach(), map(), filter(), reduce(), etc."
            });
          }
        };
      }
    }
  }
};
