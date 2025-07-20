import { addNumbers } from '../../js/script'

// Tests a single function
describe('function tests', () => {
  // An array of test scenarios to send to the function.
  const iterations = [
    {
      arg1: 3,
      arg2: 4,
      result: 7,
    },
    {
      arg1: 3,
      arg2: -4,
      result: -1,
    },{
      arg1: 30,
      arg2: 32,
      result: 62,
    }
  ];
  iterations.forEach(iteration => {
    it(`correctly adds ${iteration.arg1} + ${iteration.arg2}`, () => {
      const {arg1, arg2, result} = iteration
      expect(addNumbers(arg1, arg2)).to.equal(result)
    })
  })
})
